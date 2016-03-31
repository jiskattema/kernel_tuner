import numpy
from nose import SkipTest
from nose.tools import nottest, raises
from .context import kernel_tuner

try:
    import pycuda.driver
except Exception:
    pass

@nottest
def skip_if_no_cuda_device():
    try:
        from pycuda.autoinit import context
    #except pycuda.driver.RuntimeError, e:
    except Exception, e:
        if "No module named pycuda.autoinit" in str(e):
            raise SkipTest("PyCuda not installed")
        elif "no CUDA-capable device is detected" in str(e):
            raise SkipTest("no CUDA-capable device is detected")
        else:
            raise e

def test_create_gpu_args():

    skip_if_no_cuda_device()

    size = 1000
    a = numpy.int32(75)
    b = numpy.random.randn(size).astype(numpy.float32)
    c = numpy.zeros_like(b)

    arguments = [c, a, b]

    gpu_args = kernel_tuner._create_gpu_args(arguments)

    assert isinstance(gpu_args[0], pycuda.driver.DeviceAllocation)
    assert isinstance(gpu_args[1], numpy.int32)
    assert isinstance(gpu_args[2], pycuda.driver.DeviceAllocation)

    gpu_args[0].free()
    gpu_args[2].free()


def test_get_grid_dimensions():

    problem_size = (1024, 1024)

    params = dict()
    params["block_x"] = 41
    params["block_y"] = 37

    grid_div_x = ["block_x"]
    grid_div_y = ["block_y"]

    grid = kernel_tuner._get_grid_dimensions(problem_size, params,
                    grid_div_y, grid_div_x)

    assert len(grid) == 2
    assert isinstance(grid[0], int)
    assert isinstance(grid[1], int)

    print grid
    assert grid[0] == 25
    assert grid[1] == 28

    grid = kernel_tuner._get_grid_dimensions(problem_size, params,
                    None, grid_div_x)

    print grid
    assert grid[0] == 25
    assert grid[1] == 1024

    grid = kernel_tuner._get_grid_dimensions(problem_size, params,
                    grid_div_y, None)

    print grid
    assert grid[0] == 1024
    assert grid[1] == 28

    return grid


def test_get_thread_block_dimensions():

    params = dict()
    params["block_size_x"] = 123
    params["block_size_y"] = 257

    threads = kernel_tuner._get_thread_block_dimensions(params)
    assert len(threads) == 3
    assert isinstance(threads[0], int)
    assert isinstance(threads[1], int)
    assert isinstance(threads[2], int)

    assert threads[0] == 123
    assert threads[1] == 257
    assert threads[2] == 1

def test_prepare_kernel_string():
    kernel = "this is a weird kernel"
    params = dict()
    params["is"] = 8
    params["weird"] = 14

    new_kernel = kernel_tuner._prepare_kernel_string(kernel, params)
    assert new_kernel == "th8 8 a 14 kernel"

    new_kernel = kernel_tuner._prepare_kernel_string(kernel, dict())
    assert kernel == new_kernel

    params = dict()
    params["blablabla"] = 8
    new_kernel = kernel_tuner._prepare_kernel_string(kernel, params)
    assert kernel == new_kernel

@raises(Exception)
def test_check_restrictions1():
    params = dict()
    params["a"] = 7
    params["b"] = 4
    params["c"] = 1
    restrictions = ["a==b+c"]
    kernel_tuner._check_restrictions(restrictions, params)
    assert False

def test_check_restrictions2():
    params = dict()
    params["a"] = 7
    params["b"] = 4
    params["c"] = 3
    restrictions = ["a==b+c", "b==b", "a-b==c"]
    #test that the call does not return an exception
    try:
        kernel_tuner._check_restrictions(restrictions, params)
        assert True
    except Exception:
        assert False

