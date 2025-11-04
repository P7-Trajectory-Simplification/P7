from algorithms.test_algorithms_squish import SquishTest
from algorithms.test_algorithms_squish_e import SquishETest
from algorithms.test_algorithms_dead_reckoning import DeadReckoningTest
from algorithms.test_algorithms_douglas_peucker import DouglasPeuckerTest
from algorithms.test_algorithms_uniform_sampling import UniformSamplingTest

def run_all_tests():
    print("Running Squish Tests...")
    #squish_test = SquishTest()
    #squish_test.setUpClass()
    #squish_test.test_squish()
    #squish_test.test_run_squish()
    print("Squish Tests Passed.")

    print("Running SquishE Tests...")
    squish_e_test = SquishETest()
    squish_e_test.setUpClass()
    squish_e_test.test_squish_e()
    squish_e_test.test_run_squish_e()
    squish_e_test.test_reduce()
    squish_e_test.test_adjust_priority()
    print("SquishE Tests Passed.")

    print("Running Dead Reckoning Tests...")
    dead_reckoning_test = DeadReckoningTest()
    dead_reckoning_test.setUpClass()
    dead_reckoning_test.test_dead_reckoning()
    dead_reckoning_test.test_run_dr()
    dead_reckoning_test.test_reckon()
    print("Dead Reckoning Tests Passed.")


    print("Running Douglas-Peucker Tests...")
    douglas_peucker_test = DouglasPeuckerTest()
    douglas_peucker_test.setUpClass()
    douglas_peucker_test.test_douglas_peucker()
    douglas_peucker_test.test_run_dp()
    print("Douglas-Peucker Tests Passed.")

    print("Running Uniform Sampling Tests...")
    uniform_sampling_test = UniformSamplingTest()
    uniform_sampling_test.setUpClass()
    uniform_sampling_test.test_uniform_sampling()
    uniform_sampling_test.test_run_uniform_sampling()
    print("Uniform Sampling Tests Passed.")

if __name__ == "__main__":
    run_all_tests()