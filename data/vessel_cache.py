from datetime import datetime

from classes.cache_chunk import CacheChunk
from classes.vessel_log import VesselLog
from data.database import get_vessel_logs
from classes.vessel import Vessel

'''
vessel_log_cache structure:
{
    imo1: [
        cache_chunk1,
        cache_chunk2,
        ...
    ],
    ...
'''
vessel_log_cache = {}


def get_data_from_cache(vessel: Vessel, start_time: datetime, end_time: datetime):
    if vessel.imo not in vessel_log_cache:
        data = get_data_from_db(vessel, start_time, end_time)
        if len(data.vessel_logs) == 0:
            return []
        vessel_log_cache[vessel.imo] = [data]
        chunk = vessel_log_cache[vessel.imo][0]
    else:
        try:
            chunk = get_chunk(vessel, start_time, end_time)
        except IndexError:
            # IndexError will be thrown if chunk is empty (via call to chunk.from_date())
            return []

    return extract_segment_from_chunk(chunk, start_time, end_time)


def get_data_from_db(vessel: Vessel, start_time: datetime, end_time: datetime):
    vessel_logs = get_vessel_logs(vessel.imo, start_time, end_time)
    return CacheChunk(vessel_logs)


def get_chunk(vessel: Vessel, start_time: datetime, end_time: datetime) -> CacheChunk:
    chunks = vessel_log_cache[vessel.imo]  # type: list[CacheChunk]
    left_chunk_idx = None
    right_chunk_idx = None
    for i, chunk in enumerate(chunks):  # type: (int, CacheChunk)
        if chunk.from_date() <= start_time <= chunk.to_date():
            left_chunk_idx = i
        if chunk.from_date() <= end_time <= chunk.to_date():
            right_chunk_idx = i
        if (
            left_chunk_idx is not None and right_chunk_idx is not None
        ):  # No need to continue searching
            break

    if (
        left_chunk_idx is None and right_chunk_idx is None
    ):  # Both dates are outside cached chunks
        chunks.append(get_data_from_db(vessel, start_time, end_time))
        return chunks[-1]

    elif left_chunk_idx == right_chunk_idx:  # Both dates are in the same chunk
        return chunks[left_chunk_idx]

    elif left_chunk_idx is None:  # Only right date is in a cached chunk
        end_time = chunks[right_chunk_idx].to_date()
        del chunks[
            0 : right_chunk_idx + 1
        ]  # Remove all chunks up to and including right_chunk_idx
        chunks.insert(0, get_data_from_db(vessel, start_time, end_time))
        return chunks[0]

    elif right_chunk_idx is None:  # Only left date is in a cached chunk
        start_time = chunks[left_chunk_idx].to_date()
        del chunks[left_chunk_idx:]  # Remove all chunks from left_chunk_idx to end
        chunks.append(get_data_from_db(vessel, start_time, end_time))
        return chunks[-1]

    else:  # Both dates are in different cached chunks
        start_time = chunks[left_chunk_idx].from_date()
        end_time = chunks[right_chunk_idx].to_date()
        del chunks[
            left_chunk_idx : right_chunk_idx + 1
        ]  # Remove all chunks between left_chunk_idx and right_chunk_idx
        chunks.insert(left_chunk_idx, get_data_from_db(vessel, start_time, end_time))
        return chunks[left_chunk_idx]


def extract_segment_from_chunk(
    chunk: CacheChunk, start_time: datetime, end_time: datetime
) -> list[VesselLog]:
    left_index = None
    right_index = None
    for i, vessel_log in enumerate(chunk.vessel_logs[:-1]):
        next_vessel_log = chunk.vessel_logs[i + 1]
        if vessel_log.ts <= start_time <= next_vessel_log.ts:
            left_index = i
        if vessel_log.ts <= end_time <= next_vessel_log.ts:
            right_index = i
        if left_index is not None and right_index is not None:
            break

    start = 0 if left_index is None else left_index
    end = right_index + 1 if right_index is not None else None
    return chunk.vessel_logs[start:end]
