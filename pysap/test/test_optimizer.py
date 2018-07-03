# -*- coding: utf-8 -*-
##########################################################################
# pySAP - Copyright (C) CEA, 2017 - 2018
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from __future__ import print_function
import unittest
# import os
import numpy
from scipy.fftpack import fftshift
from modopt.math.metrics import mse, ssim
# import sys
# import time

# Package import
import pysap
from pysap.plugins.mri.reconstruct.linear import Wavelet2
from pysap.plugins.mri.reconstruct.fourier import FFT2, NFFT2
from pysap.plugins.mri.reconstruct_3D.fourier import NUFFT, FFT3
from pysap.plugins.mri.reconstruct.gradient import GradAnalysis2
from pysap.plugins.mri.reconstruct.gradient import GradSynthesis2
from pysap.plugins.mri.parallel_mri.reconstruct import sparse_rec_fista
from pysap.plugins.mri.reconstruct.utils import convert_mask_to_locations
from pysap.plugins.mri.parallel_mri.reconstruct import sparse_rec_condatvu
import pysap.extensions.transform
import warnings
from pysap.data import get_sample_data


class TestOptimizer(unittest.TestCase):
    """ Test the FISTA's gradient descent.
    """
    def setUp(self):
        """ Get the data from the server.
        """
        self.images = [
            # get_sample_data(dataset_name="astro-fits"),
            get_sample_data(dataset_name="mri-slice-nifti")]
        print("[info] Image loaded for test: {0}.".format(
            [i.data.shape for i in self.images]))
        self.mask = get_sample_data("mri-mask").data
        self.names = ['BsplineWaveletTransformATrousAlgorithm']
        print("[info] Found {0} transformations.".format(len(self.names)))
        self.nb_scales = [4]  # [2, 3, 4]
        self.nb_iter = 300

    def test_reconstruction_fista_fft2(self):
        """ Test all the registered transformations.
        """
        print('Process test FFT2 FISTA')
        for image in self.images:
            fourier = FFT2(samples=convert_mask_to_locations(
                                            fftshift(self.mask)),
                           shape=image.shape)
            data = fourier.op(image.data)
            fourier_op = FFT2(convert_mask_to_locations(
                                            fftshift(self.mask)),
                              shape=image.shape)
            print("Process test with image '{0}'...".format(
                image.metadata["path"]))
            for nb_scale in self.nb_scales:
                print("- Number of scales: {0}".format(nb_scale))
                for name in self.names:
                    print("    Transform: {0}".format(name))
                    linear_op = Wavelet2(wavelet_name=name,
                                         nb_scale=nb_scale)
                    gradient_op = GradSynthesis2(data=data,
                                                 fourier_op=fourier_op,
                                                 linear_op=linear_op)
                    x_final, transform = sparse_rec_fista(
                                            gradient_op=gradient_op,
                                            linear_op=linear_op,
                                            mu=0,
                                            lambda_init=1.0,
                                            max_nb_of_iter=self.nb_iter,
                                            atol=1e-4,
                                            verbose=0,
                                            get_cost=False)

                    print('MSE value: ', mse(x_final, fourier.adj_op(data)))
                    print('SSIM Value: ', ssim(x_final, fourier.adj_op(data),
                                               mask=None))
                    mismatch = (1. - numpy.mean(
                        numpy.isclose(x_final, fourier.adj_op(data),
                                      rtol=1e-3)))
                    print("      mismatch = ", mismatch)
                    self.assertTrue(mismatch == 0.0)

    def test_reconstruction_condat_vu_fft2(self):
        """ Test all the registered transformations.
        """
        print('Process test FFT2 Condat Vu algorithm')
        for image in self.images:
            fourier = FFT2(samples=convert_mask_to_locations(
                                fftshift(self.mask)), shape=image.shape)
            data = fourier.op(image.data)
            fourier_op = FFT2(samples=convert_mask_to_locations(
                                fftshift(self.mask)), shape=image.shape)
            print("Process test with image '{0}'...".format(
                image.metadata["path"]))
            for nb_scale in self.nb_scales:
                print("- Number of scales: {0}".format(nb_scale))
                for name in self.names:
                    print("    Transform: {0}".format(name))
                    linear_op = Wavelet2(wavelet_name=name,
                                         nb_scale=nb_scale)
                    gradient_op = GradAnalysis2(data=data,
                                                fourier_op=fourier_op)
                    x_final, transform = sparse_rec_condatvu(
                                            gradient_op=gradient_op,
                                            linear_op=linear_op,
                                            std_est=0.0,
                                            std_est_method="dual",
                                            std_thr=0,
                                            mu=0,
                                            tau=None,
                                            sigma=None,
                                            relaxation_factor=1.0,
                                            nb_of_reweights=0,
                                            max_nb_of_iter=self.nb_iter,
                                            add_positivity=False,
                                            atol=1e-4,
                                            verbose=0)
                    print('MSE value: ', mse(x_final, fourier.adj_op(data)))
                    print('SSIM Value: ', ssim(x_final, fourier.adj_op(data),
                                               mask=None))
                    mismatch = (1. - numpy.mean(
                        numpy.isclose(x_final, fourier.adj_op(data),
                                      rtol=1e-3)))
                    print("      mismatch = ", mismatch)
                    self.assertTrue(mismatch == 0.0)

    def test_reconstruction_fista_nfft2(self):
        """ Test all the registered transformations.
        """
        warnings.warn('No test will be made on the NFFT package')
        # print('Process test NFFT2 FISTA')
        # for image in self.images:
        #     fourier = FFT2(samples=convert_mask_to_locations(
        #                                     fftshift(self.mask)),
        #                    shape=image.shape)
        #     data_fft = fourier.op(image)
        #     fourier_gen = NFFT2(samples=convert_mask_to_locations(
        #                                     self.mask),
        #                         shape=image.shape)
        #     data = fourier_gen.op(image.data)
        #     fourier_op = NFFT2(convert_mask_to_locations(
        #                                     self.mask),
        #                        shape=image.shape)
        #     print("Process test with image '{0}'...".format(
        #         image.metadata["path"]))
        #     for nb_scale in self.nb_scales:
        #         print("- Number of scales: {0}".format(nb_scale))
        #         for name in self.names:
        #             print("    Transform: {0}".format(name))
        #             linear_op = Wavelet2(wavelet_name=name,
        #                                  nb_scale=nb_scale)
        #             gradient_op = GradSynthesis2(data=data,
        #                                          fourier_op=fourier_op,
        #                                          linear_op=linear_op)
        #             x_final, transform = sparse_rec_fista(
        #                                     gradient_op=gradient_op,
        #                                     linear_op=linear_op,
        #                                     mu=0,
        #                                     lambda_init=1.0,
        #                                     max_nb_of_iter=self.nb_iter,
        #                                     atol=1e-4,
        #                                     verbose=0,
        #                                     get_cost=False)
        #             I_0 = fourier.adj_op(data_fft)
        #             print('MSE value: ', mse(x_final, I_0))
        #             print('SSIM Value: ', ssim(x_final,
        #                                        I_0,
        #                                        mask=None))
        #
        #             mismatch = (1. - numpy.mean(
        #                 numpy.isclose(x_final, I_0,
        #                               rtol=1e-3)))
        #             print("      mismatch = ", mismatch)
        #             self.assertTrue(mismatch == 0.0)

    def test_reconstruction_condat_vu_nfft2(self):
        """ Test all the registered transformations.
        """
        warnings.warn('No test will be made on the NFFT package')
        # print('Process test NFFT2 Condat Vu algorithm')
        # for image in self.images:
        #     fourier = FFT2(samples=convert_mask_to_locations(
        #                         fftshift(self.mask)), shape=image.shape)
        #     data_fft = fourier.op(image.data)
        #     fourier_gen = NFFT2(samples=convert_mask_to_locations(
        #                         self.mask), shape=image.shape)
        #     data = fourier_gen.op(image.data)
        #     fourier_op = NFFT2(samples=convert_mask_to_locations(
        #                         self.mask), shape=image.shape)
        #     print("Process test with image '{0}'...".format(
        #         image.metadata["path"]))
        #     for nb_scale in self.nb_scales:
        #         print("- Number of scales: {0}".format(nb_scale))
        #         for name in self.names:
        #             print("    Transform: {0}".format(name))
        #             linear_op = Wavelet2(wavelet_name=name,
        #                                  nb_scale=nb_scale)
        #             gradient_op = GradAnalysis2(data=data,
        #                                         fourier_op=fourier_op)
        #             x_final, transform = sparse_rec_condatvu(
        #                                     gradient_op=gradient_op,
        #                                     linear_op=linear_op,
        #                                     std_est=0.0,
        #                                     std_est_method="dual",
        #                                     std_thr=0,
        #                                     mu=0,
        #                                     tau=None,
        #                                     sigma=None,
        #                                     relaxation_factor=1.0,
        #                                     nb_of_reweights=0,
        #                                     max_nb_of_iter=self.nb_iter,
        #                                     add_positivity=False,
        #                                     atol=1e-4,
        #                                     verbose=0)
        #             I_0 = fourier.adj_op(data_fft)
        #             print('MSE value: ', mse(x_final, I_0))
        #             print('SSIM Value: ', ssim(x_final,
        #                                        I_0,
        #                                        mask=None))
        #             mismatch = (1. - numpy.mean(
        #                 numpy.isclose(x_final, I_0,
        #                               rtol=1e-3)))
        #             print("      mismatch = ", mismatch)
        #             self.assertTrue(mismatch == 0.0)

    def test_reconstruction_fista_nufft(self):
        """ Test all the registered transformations.
        """
        warnings.warn('No test will be made on the NUFFT package')
        # print('Process test NUFFT2 FISTA')
        # for image in self.images:
        #     fourier = FFT2(samples=convert_mask_to_locations(
        #                                     numpy.fft.fftshift(self.mask)),
        #                    shape=image.shape)
        #     data_fft = fourier.op(image.data)
        #     fourier_op_gen = NUFFT(samples=convert_mask_to_locations(
        #                                     self.mask),
        #                            shape=image.shape,
        #                            platform='cpu',
        #                            Kd=image.shape,
        #                            Jd=1)
        #     data = fourier_op_gen.op(image.data)
        #     fourier_op = NUFFT(samples=convert_mask_to_locations(
        #                                     self.mask),
        #                        shape=image.shape,
        #                        platform='cpu',
        #                        Kd=image.shape,
        #                        Jd=1)
        #
        #     print("Process test with image '{0}'...".format(
        #         image.metadata["path"]))
        #     for nb_scale in self.nb_scales:
        #         print("- Number of scales: {0}".format(nb_scale))
        #         for name in self.names:
        #             print("    Transform: {0}".format(name))
        #             linear_op = Wavelet2(wavelet_name=name,
        #                                  nb_scale=nb_scale)
        #             gradient_op = GradSynthesis2(data=data,
        #                                          fourier_op=fourier_op,
        #                                          linear_op=linear_op)
        #             x_final, transform = sparse_rec_fista(
        #                                     gradient_op=gradient_op,
        #                                     linear_op=linear_op,
        #                                     mu=0,
        #                                     lambda_init=1.0,
        #                                     max_nb_of_iter=self.nb_iter,
        #                                     atol=1e-4,
        #                                     verbose=0,
        #                                     get_cost=False)
        #             I_0 = fourier.adj_op(data_fft)
        #             print('MSE value: ', mse(x_final, I_0))
        #             print('SSIM Value: ', ssim(x_final, I_0,
        #                                        mask=None))
        #             mismatch = (1. - numpy.mean(
        #                 numpy.isclose(x_final, I_0,
        #                               rtol=1e-3)))
        #             print("      mismatch = ", mismatch)
        #             self.assertTrue(mismatch == 0.0)


if __name__ == "__main__":
    unittest.main()
