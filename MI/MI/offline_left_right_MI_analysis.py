import argparse
import numpy as np
import mne
import pyxdf
import matplotlib.pyplot as plt
from mne.time_frequency import psd_array_welch, tfr_array_morlet
from scipy.signal import spectrogram
from mnelab.io.xdf import read_raw_xdf
from mindcontrolrobots.utils.marker import OutletMIMarker
import os
from scipy.io import savemat

# Frequency bands
MU_BAND = (8, 13)  # Mu rhythm
BETA_BAND = (13, 30)  # Beta rhythm

LABEL_MAP = {
    0: ("Open Eye Rest", OutletMIMarker.START_OPEN_EYE_REST, OutletMIMarker.END_OPEN_EYE_REST),
    1: ("Close Eye Rest", OutletMIMarker.START_CLOSE_EYE_REST, OutletMIMarker.END_CLOSE_EYE_REST),
    2: ("Left MI", OutletMIMarker.START_LEFT, OutletMIMarker.END_LEFT),
    3: ("Right MI", OutletMIMarker.START_RIGHT, OutletMIMarker.END_RIGHT),
}

def apply_car(data, ch_names):
    """Apply Common Average Reference (CAR) using MNE's set_eeg_reference."""
    # Create a temporary RawArray object
    info = mne.create_info(ch_names=ch_names, sfreq=1, ch_types='eeg')
    raw = mne.io.RawArray(data, info)
    
    # Apply CAR using MNE's function
    raw_car = raw.copy().set_eeg_reference('average')
    
    # Get the data back
    car_data = raw_car.get_data()
    return car_data

def calculate_erd_ers(data, sfreq, baseline_duration=0.5):
    """Calculate ERD/ERS using the first baseline_duration seconds as baseline."""
    baseline_samples = int(baseline_duration * sfreq)
    baseline = np.mean(data[:, :baseline_samples], axis=1)
    erd = (data - baseline[:, np.newaxis]) / baseline[:, np.newaxis] * 100
    return erd

def save_individual_plots(all_epochs_data, all_epochs_timestamps, sfreq, ch_names, output_dir="./"):
    for label, trials in all_epochs_data.items():
        label_name = LABEL_MAP[label][0]
        label_dir = os.path.join(output_dir, label_name.lower())
        os.makedirs(label_dir, exist_ok=True)

        for i, data in enumerate(trials):
            timestamps = all_epochs_timestamps[label][i]
            time = timestamps - timestamps[0]

            try:
                c3_idx = ch_names.index("C3")
                c4_idx = ch_names.index("C4")
            except ValueError:
                continue

            # Apply CAR
            car_data = apply_car(data, ch_names)

            # Calculate PSD
            psd_full, freqs = psd_array_welch(data * 1e6, sfreq, fmin=1, fmax=40, verbose=False)
            psd_db = 10 * np.log10(psd_full)

            # Calculate power in frequency bands
            mu_power_c3 = np.mean(psd_full[c3_idx, (freqs >= MU_BAND[0]) & (freqs <= MU_BAND[1])])
            mu_power_c4 = np.mean(psd_full[c4_idx, (freqs >= MU_BAND[0]) & (freqs <= MU_BAND[1])])
            beta_power_c3 = np.mean(psd_full[c3_idx, (freqs >= BETA_BAND[0]) & (freqs <= BETA_BAND[1])])
            beta_power_c4 = np.mean(psd_full[c4_idx, (freqs >= BETA_BAND[0]) & (freqs <= BETA_BAND[1])])

            # Create figure with 1 row and 5 columns
            fig, axes = plt.subplots(1, 5, figsize=(25, 5))
            fig.suptitle(f"{label_name} Trial {i+1} - Motor Imagery Analysis")

            # Plot 1: CAR EEG (C3)
            car_c3 = car_data[c3_idx] * 1e6
            axes[0].plot(time, car_c3, color='blue')
            axes[0].set_title("CAR EEG - C3")
            axes[0].set_xlabel("Time (s)")
            axes[0].set_ylabel("Amplitude (μV)")

            # Plot 2: CAR EEG (C4)
            car_c4 = car_data[c4_idx] * 1e6
            axes[1].plot(time, car_c4, color='red')
            axes[1].set_title("CAR EEG - C4")
            axes[1].set_xlabel("Time (s)")
            axes[1].set_ylabel("Amplitude (μV)")

            # Plot 3: Power Values
            bars = axes[2].bar(['C3 Mu', 'C4 Mu', 'C3 Beta', 'C4 Beta'],
                             [mu_power_c3, mu_power_c4, beta_power_c3, beta_power_c4],
                             color=['blue', 'red', 'blue', 'red'])
            axes[2].set_title("Power in Frequency Bands")
            axes[2].set_ylabel("Power (μV)")
            for bar in bars:
                height = bar.get_height()
                axes[2].text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2e}',
                           ha='center', va='bottom')

            # Plot 4: Spectrogram (C3)
            f, t, Sxx = spectrogram(data[c3_idx] * 1e6, sfreq, nperseg=128, noverlap=64)
            f_masked = f[f <= 40]
            Sxx_masked = Sxx[f <= 40, :]
            axes[3].pcolormesh(t, f_masked, Sxx_masked, shading='gouraud', cmap='viridis')
            axes[3].set_title("C3 Spectrogram")
            axes[3].set_xlabel("Time (s)")
            axes[3].set_ylabel("Frequency (Hz)")
            axes[3].set_ylim(0, 40)

            # Plot 5: PSD
            axes[4].plot(freqs, psd_db[c3_idx], label='C3', color='blue')
            axes[4].plot(freqs, psd_db[c4_idx], label='C4', color='red')
            axes[4].axvspan(*MU_BAND, color='gray', alpha=0.3, label='Mu Band')
            axes[4].axvspan(*BETA_BAND, color='green', alpha=0.3, label='Beta Band')
            axes[4].set_title("Power Spectral Density")
            axes[4].set_xlabel("Frequency (Hz)")
            axes[4].set_ylabel("Power (dB)")
            axes[4].legend()

            plt.tight_layout()
            fig_path = os.path.join(label_dir, f"trial_{i+1}.png")
            plt.savefig(fig_path, dpi=300)
            plt.close()
            mat_path = fig_path.replace(".png", ".mat")
            savemat(mat_path, {
                "mu_power_c3": mu_power_c3,
                "mu_power_c4": mu_power_c4,
                "beta_power_c3": beta_power_c3,
                "beta_power_c4": beta_power_c4
            })

def plot_summary(eeg_data_dict, timestamps_dict, sfreq, ch_names, output_path="eeg_summary.png"):
    # Create figure with 3 rows (rest, right, left) and 5 columns
    fig, axes = plt.subplots(3, 5, figsize=(25, 15))
    fig.suptitle("Motor Imagery Analysis Summary")

    # Define the order of conditions
    conditions = [(0, "Rest"), (2, "Right"), (1, "Left")]

    for row, (label, label_name) in enumerate(conditions):
        eeg_data = eeg_data_dict[label]
        timestamps = timestamps_dict[label]
        if eeg_data is None or timestamps is None:
            continue

        try:
            c3_idx = ch_names.index("C3")
            c4_idx = ch_names.index("C4")
        except ValueError:
            print("C3 or C4 not found.")
            continue

        # Apply CAR
        car_data = apply_car(eeg_data, ch_names)
        time = timestamps - timestamps[0]

        # Calculate PSD
        psd_full, freqs = psd_array_welch(eeg_data * 1e6, sfreq, fmin=1, fmax=40)
        psd_db = 10 * np.log10(psd_full)

        # Calculate power in frequency bands
        mu_power_c3 = np.mean(psd_full[c3_idx, (freqs >= MU_BAND[0]) & (freqs <= MU_BAND[1])])
        mu_power_c4 = np.mean(psd_full[c4_idx, (freqs >= MU_BAND[0]) & (freqs <= MU_BAND[1])])
        beta_power_c3 = np.mean(psd_full[c3_idx, (freqs >= BETA_BAND[0]) & (freqs <= BETA_BAND[1])])
        beta_power_c4 = np.mean(psd_full[c4_idx, (freqs >= BETA_BAND[0]) & (freqs <= BETA_BAND[1])])

        # Plot 1: CAR EEG (C3)
        car_c3 = car_data[c3_idx] * 1e6
        axes[row, 0].plot(time, car_c3, color='blue')
        axes[row, 0].set_title(f"CAR EEG - C3 ({label_name})")
        axes[row, 0].set_xlabel("Time (s)")
        axes[row, 0].set_ylabel("Amplitude (μV)")

        # Plot 2: CAR EEG (C4)
        car_c4 = car_data[c4_idx] * 1e6
        axes[row, 1].plot(time, car_c4, color='red')
        axes[row, 1].set_title(f"CAR EEG - C4 ({label_name})")
        axes[row, 1].set_xlabel("Time (s)")
        axes[row, 1].set_ylabel("Amplitude (μV)")

        # Plot 3: Power Values
        bars = axes[row, 2].bar(['C3 Mu', 'C4 Mu', 'C3 Beta', 'C4 Beta'],
                              [mu_power_c3, mu_power_c4, beta_power_c3, beta_power_c4],
                              color=['blue', 'red', 'blue', 'red'])
        axes[row, 2].set_title(f"Power in Frequency Bands - {label_name}")
        axes[row, 2].set_ylabel("Power (μV?)")
        for bar in bars:
            height = bar.get_height()
            axes[row, 2].text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2e}',
                            ha='center', va='bottom')

        # Plot 4: Spectrogram (C3)
        f, t, Sxx = spectrogram(eeg_data[c3_idx] * 1e6, sfreq, nperseg=128, noverlap=64)
        f_masked = f[f <= 40]
        Sxx_masked = Sxx[f <= 40, :]
        axes[row, 3].pcolormesh(t, f_masked, Sxx_masked, shading='gouraud', cmap='viridis')
        axes[row, 3].set_title(f"C3 Spectrogram - {label_name}")
        axes[row, 3].set_xlabel("Time (s)")
        axes[row, 3].set_ylabel("Frequency (Hz)")
        axes[row, 3].set_ylim(0, 40)

        # Plot 5: PSD
        axes[row, 4].plot(freqs, psd_db[c3_idx], label='C3', color='blue')
        axes[row, 4].plot(freqs, psd_db[c4_idx], label='C4', color='red')
        axes[row, 4].axvspan(*MU_BAND, color='gray', alpha=0.3, label='Mu Band')
        axes[row, 4].axvspan(*BETA_BAND, color='green', alpha=0.3, label='Beta Band')
        axes[row, 4].set_title(f"Power Spectral Density - {label_name}")
        axes[row, 4].set_xlabel("Frequency (Hz)")
        axes[row, 4].set_ylabel("Power (dB)")
        axes[row, 4].legend()

    plt.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close()
    print(f"\n Summary saved to {output_path}")

def plot_topomaps(eeg_data_dict, timestamps_dict, sfreq, ch_names, output_path="eeg_topomaps.png"):
    # Create figure with 4 rows (timeline + 3 conditions) and 11 columns (10 time points + 1 colorbar)
    fig, axes = plt.subplots(4, 11, figsize=(40, 20))
    fig.suptitle("Motor Imagery Power Analysis")

    # Define the order of conditions
    conditions = [(0, "Rest"), (2, "Right"), (1, "Left")]

    # Remove unwanted channels from ch_names
    channels_to_remove = ['Gyro-x', 'Gyro-y', 'Gyro-z', 'Acc-x', 'Acc-y', 'Acc-z', 'FCZ', 'CZ']
    cleaned_ch_names = [ch for ch in ch_names if ch not in channels_to_remove]
    
    # Create info object for topomap with the cleaned channels
    info = mne.create_info(cleaned_ch_names, sfreq=sfreq, ch_types='eeg')
    montage = mne.channels.make_standard_montage('standard_1020')
    info.set_montage(montage, on_missing='ignore')

    # Modify positions of FCZ and CZ if they are still included
    if 'FCZ' in info['ch_names'] and 'CZ' in info['ch_names']:
        info.get_positions()['ch_pos']['FCZ'] = [0.0, 0.0, 0.05]  # Example position for FCZ
        info.get_positions()['ch_pos']['CZ'] = [0.0, 0.0, 0.10]   # Example position for CZ
        print("Adjusted positions for FCZ and CZ.")

    # Find the minimum length across all conditions
    min_length = float('inf')
    for label, _ in conditions:
        if eeg_data_dict[label] is not None:
            min_length = min(min_length, eeg_data_dict[label].shape[1])

    if min_length == float('inf'):
        print("No valid data for topomap analysis")
        return

    # Calculate time points within the common window - now 10 points
    time_points = np.linspace(0, min_length-1, 10, dtype=int)
    time_sec = time_points / sfreq  # Convert to seconds

    # Plot timeline at the top
    for i, t in enumerate(time_sec):
        axes[0, i].text(0.5, 0.5, f"t = {t:.1f}s", 
                       ha='center', va='center', fontsize=12)
        axes[0, i].axis('off')
    axes[0, 10].axis('off')  # Hide the colorbar axis in the timeline row

    # Plot topomaps for each condition
    for row, (label, label_name) in enumerate(conditions, start=1):
        eeg_data = eeg_data_dict[label]
        if eeg_data is None:
            continue

        # Calculate time-frequency power in mu band
        freqs = np.arange(MU_BAND[0], MU_BAND[1] + 1)
        n_cycles = freqs / 2
        
        # Reshape data for tfr_array_morlet
        data_reshaped = (eeg_data[:, :min_length] * 1e6)[np.newaxis, :, :]
        
        # Compute time-frequency power
        power = mne.time_frequency.tfr_array_morlet(
            data_reshaped, sfreq, freqs, n_cycles=n_cycles,
            output='power', decim=1
        )
        
        # Get power in mu band by averaging across frequencies (axis=1)
        mu_power = np.mean(np.abs(power[0]), axis=1)  # Average across frequencies

        # Ensure that mu_power only has the same number of channels as in 'info' (8 channels)
        mu_power = mu_power[:len(info['ch_names'])]  # Slice mu_power to match the info channels
        
        # Create evoked array for all time points
        evoked = mne.EvokedArray(
            mu_power,  # Now shape is (n_channels, n_times)
            info,
            tmin=0,
            nave=1
        )
        
        # Plot all topomaps at once with colorbar
        evoked.plot_topomap(
            times=time_sec,  # All time points at once
            axes=axes[row, :],  # All axes for this row including colorbar
            show=False,
            cmap='viridis',  # Use viridis colormap for power
            contours=6,
            sensors=True,
            time_unit='s',
            size=2,
            extrapolate='head',
            sphere=(0, 0, 0, 0.09),  # Standard head sphere
            show_names=True,  # Show channel names
            mask=None,  # No masking
            mask_params=None,  # No mask parameters
            outlines='head',  # Show head outline
            border='mean',  # Border style
            res=64,  # Resolution
            image_interp='cubic',  # Interpolation method
            units='μV',  # Set units to power
            scalings=dict(eeg=1),  # No scaling needed
            colorbar=True  # Show colorbar
        )
        
        # Set titles for each subplot
        for i in range(10):  # Only set titles for the topomap axes
            axes[row, i].set_title(f"{label_name}")

    plt.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close()
    print(f"\n mu  Power Topomaps saved to {output_path}")


def main(args):
    print(f"\n? Loading XDF file: {args.xdf_file}")
    streams = pyxdf.resolve_streams(args.xdf_file)  # Resolves streams from the XDF file
    stream_ids = pyxdf.match_streaminfos(streams, [{"type": "EEG"}])  # Matches streams based on the type (EEG)
    
    # Now you can load the raw EEG data using stream_ids
    raw = read_raw_xdf(args.xdf_file, stream_ids)
    
    # Apply filters
    raw.filter(l_freq=1, h_freq=50)
    raw.notch_filter(60)
    
    # Plot raw data
    raw.plot()
    plt.show()
    
    unit_code = raw.info["chs"][0]["unit"]
    print("Unit code:", unit_code)

    sfreq = raw.info["sfreq"]
    events, event_id = mne.events_from_annotations(raw)

    # Get all EEG channels
    raw.pick_types(eeg=True)
    ch_names = raw.ch_names
    print(f"Available EEG channels: {ch_names}")
    print("Number of channels:", len(ch_names))
    print("Channel names:", ch_names)

    # Create output directory
    xdf_name = os.path.splitext(os.path.basename(args.xdf_file))[0]  # Create output directory name
    output_dir = os.path.join(os.getcwd(), "offline_analyze", xdf_name)
    os.makedirs(output_dir, exist_ok=True)

    # Analyze and save everything
    integrate_offline_plotting(raw, events, event_id, sfreq, ch_names, output_dir=output_dir)

def integrate_offline_plotting(raw, events, event_id, sfreq, ch_names, output_dir="./"):
    all_epochs_data = {}
    all_epochs_timestamps = {}

    for label, (label_name, start_marker, end_marker) in LABEL_MAP.items():
        start_code = event_id[start_marker.value]
        end_code = event_id[end_marker.value]

        start_idx = np.where(events[:, 2] == start_code)[0]
        end_idx = np.where(events[:, 2] == end_code)[0]

        if len(start_idx) == 0 or len(end_idx) == 0:
            print(f"??  Missing markers: {start_marker}, {end_marker}")
            all_epochs_data[label] = []
            all_epochs_timestamps[label] = []
            continue

        epochs_list = []
        timestamps_list = []

        tmax = (events[end_idx[0], 0] - events[start_idx[0], 0]) / sfreq
        epoch = mne.Epochs(raw, events, event_id={start_marker.value: start_code}, 
                          tmin=0, tmax=tmax, baseline=None, detrend=None, preload=True)
        data = epoch.get_data()  # Get all channels, not just C3 and C4
        timestamps = epoch.times + epoch.events[0, 0] / sfreq
        for i in range(data.shape[0]):
            epochs_list.append(data[i])
            timestamps_list.append(timestamps)
        all_epochs_data[label] = epochs_list
        all_epochs_timestamps[label] = timestamps_list

    save_individual_plots(all_epochs_data, all_epochs_timestamps, sfreq, ch_names, output_dir)

    # Compute and plot summary
    avg_data = {}
    avg_timestamps = {}

    for label in all_epochs_data:
        trials = all_epochs_data[label]
        timestamps_list = all_epochs_timestamps[label]

        if len(trials) == 0:
            avg_data[label] = None
            avg_timestamps[label] = None
            continue

        # Find the minimum trial length
        min_len = min(trial.shape[1] for trial in trials)

        # Crop all trials to min length
        trials_cropped = np.array([trial[:, :min_len] for trial in trials])
        timestamps_cropped = timestamps_list[0][:min_len]

        avg_data[label] = np.mean(trials_cropped, axis=0)
        avg_timestamps[label] = timestamps_cropped

    # Plot summary and topomaps
    plot_summary(avg_data, avg_timestamps, sfreq, ch_names, 
                output_path=os.path.join(output_dir, "eeg_summary.png"))
    plot_topomaps(avg_data, avg_timestamps, sfreq, ch_names,
                 output_path=os.path.join(output_dir, "eeg_topomaps.png"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline MI EEG Analysis")
    parser.add_argument("--xdf_file", type=str, required=True, help="Path to the XDF file.")
    args = parser.parse_args()
    main(args)
