"""
Tests for kernel objects.
"""

# pylint: disable=missing-docstring

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import numpy as np
import numpy.testing as nt
import scipy.optimize as spop
import nose

import reggie.kernels as kernels


### BASE TEST CLASSES #########################################################

class KernelTest(object):
    def __init__(self, kernel, X1, X2):
        self.kernel = kernel
        self.X1 = X1
        self.X2 = X2

    def test_repr(self):
        _ = repr(self.kernel)

    def test_call(self):
        m = self.X1.shape[0]
        n = self.X2.shape[0]
        K = self.kernel.get_kernel(self.X1, self.X2)
        K_ = np.array([self.kernel(x1, x2)
                       for x1 in self.X1
                       for x2 in self.X2]).reshape(m, n)
        nt.assert_equal(K, K_)

    def test_get_kernel(self):
        K = self.kernel.get_kernel(self.X1, self.X1)
        k = self.kernel.get_dkernel(self.X1)
        nt.assert_allclose(k, K.diagonal())

    def test_get_dgrad(self):
        g = np.array(list(self.kernel.get_dgrad(self.X1)))
        G = np.array([_.diagonal() for _ in self.kernel.get_grad(self.X1,
                                                                 self.X1)])
        nt.assert_allclose(g, G)

    def test_get_grad(self):
        x = self.kernel.params.get_value()
        k = lambda x, x1, x2: self.kernel.copy(x)(x1, x2)

        G = np.array(list(self.kernel.get_grad(self.X1, self.X2)))
        m = self.X1.shape[0]
        n = self.X2.shape[0]

        G_ = np.array([spop.approx_fprime(x, k, 1e-8, x1, x2)
                       for x1 in self.X1
                       for x2 in self.X2]).swapaxes(0, 1).reshape(-1, m, n)

        nt.assert_allclose(G, G_, rtol=1e-6, atol=1e-6)


class RealKernelTest(KernelTest):
    def __init__(self, kernel):
        rng = np.random.RandomState(0)
        X1 = rng.rand(5, kernel.ndim)
        X2 = rng.rand(3, kernel.ndim)
        super(RealKernelTest, self).__init__(kernel, X1, X2)

    def test_get_gradx(self):
        G1 = self.kernel.get_gradx(self.X1, self.X2)
        m = self.X1.shape[0]
        n = self.X2.shape[0]
        d = self.X1.shape[1]
        k = self.kernel

        G2 = np.array([spop.approx_fprime(x1, k, 1e-8, x2)
                       for x1 in self.X1
                       for x2 in self.X2]).reshape(m, n, d)

        nt.assert_allclose(G1, G2, rtol=1e-6, atol=1e-6)

    def test_gradxy(self):
        try:
            G1 = self.kernel.get_gradxy(self.X1, self.X2)
        except NotImplementedError:
            raise nose.SkipTest()

        m = self.X1.shape[0]
        n = self.X2.shape[0]
        d = self.X1.shape[1]
        g = lambda x2, x1, i: self.kernel.get_gradx(x1[None],
                                                    x2[None])[0, 0, i]

        G2 = np.array([spop.approx_fprime(x2, g, 1e-8, x1, i)
                       for x1 in self.X1
                       for x2 in self.X2
                       for i in range(d)]).reshape(m, n, d, d)

        nt.assert_allclose(G1, G2, rtol=1e-6, atol=1e-6)

    def test_sample_spectrum(self):
        try:
            W, alpha = self.kernel.sample_spectrum(100)
        except NotImplementedError:
            raise nose.SkipTest()
        assert W.shape == (100, self.kernel.ndim)
        assert isinstance(alpha, float)


### INIT TESTS ################################################################

def test_matern():
    nt.assert_raises(ValueError, kernels.Matern, 1, 1, d=12)


### PER-INSTANCE TEST CLASSES #################################################

class TestSEIso(RealKernelTest):
    def __init__(self):
        RealKernelTest.__init__(self, kernels.SE(0.8, 0.3, ndim=2))


class TestSEARD(RealKernelTest):
    def __init__(self):
        RealKernelTest.__init__(self, kernels.SE(0.8, [0.3, 0.4]))


class TestMatern1Iso(RealKernelTest):
    def __init__(self):
        RealKernelTest.__init__(self, kernels.Matern(0.8, 0.3, d=1, ndim=2))


class TestMatern3Iso(RealKernelTest):
    def __init__(self):
        RealKernelTest.__init__(self, kernels.Matern(0.8, 0.3, d=3, ndim=2))


class TestMatern5Iso(RealKernelTest):
    def __init__(self):
        RealKernelTest.__init__(self, kernels.Matern(0.8, 0.3, d=5, ndim=2))


class TestMatern1ARD(RealKernelTest):
    def __init__(self):
        RealKernelTest.__init__(self, kernels.Matern(0.8, [0.3, 0.4], d=1))


class TestMatern3ARD(RealKernelTest):
    def __init__(self):
        RealKernelTest.__init__(self, kernels.Matern(0.8, [0.3, 0.4], d=3))


class TestMatern5ARD(RealKernelTest):
    def __init__(self):
        RealKernelTest.__init__(self, kernels.Matern(0.8, [0.3, 0.4], d=5))
