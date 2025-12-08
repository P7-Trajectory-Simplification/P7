import json
import os
from datetime import timedelta

from classes.vessel_log import VesselLog
from experiments.experiment_template import slurm_template


class Job:
    def __init__(
        self,
        trajectory: list[VesselLog],
        alg: str,
        params: dict[str, int | float],
        math: str,
        additional_info: str = "",
    ):
        self.imo = trajectory[0].imo

        # To include first log of the trajectory
        self.start_ts = trajectory[0].ts - timedelta(minutes=1)
        self.end_ts = trajectory[-1].ts
        self.alg = alg
        self.params = params
        self.math = math
        self.additional_info = additional_info

    def get_short_start(self):
        return self.start_ts.strftime("%Y_%m_%d")  # "2024_01_01"

    def get_short_end(self):
        return self.end_ts.strftime("%Y_%m_%d")  # "2025_01_31"

    def get_iso_start(self):
        return self.start_ts.isoformat()

    def get_iso_end(self):
        return self.end_ts.isoformat()

    def get_params_json_str(self):
        return json.dumps(self.params).replace('"', '\\"')

    def generate_template(self, tag: str, log_dir: str, data_file_path: str) -> str:
        return slurm_template.format(
            log_dir=log_dir,
            tag=tag,
            data_file_path=data_file_path,
            alg=self.alg,
            params=self.get_params_json_str(),
            math=self.math,
        )

    def generate_job(self, directory_name: str, data_file_path: str, idx: int):
        tag = f"{idx}_{self.additional_info}"
        if self.additional_info == "":
            tag = f"{idx}"
        filepath = os.path.join(directory_name, f"job_{tag}.sh")
        log_dir = os.path.join(directory_name, "logs")
        filepath = filepath.replace("\\", "/")
        log_dir = log_dir.replace("\\", "/")
        data_file_path = data_file_path.replace("\\", "/")
        template = self.generate_template(tag, log_dir, data_file_path)

        with open(filepath, "w+", newline="\n") as f:
            f.write(template)
