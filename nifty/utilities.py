import time


def time_execution(in_function, *args, in_loop_count=1, **kwargs):

	start_time = time.perf_counter()
	for _ in range(in_loop_count):
		result = in_function(*args, **kwargs)

	end_time = time.perf_counter()
	time_taken = end_time - start_time
	print(f"{in_loop_count} execution(s) of '{in_function.__name__}' took: {time_taken} seconds")

	return result
