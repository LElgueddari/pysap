"""
Neuroimaging cartesian reconstruction
=====================================

Credit: L Elgueddari

In this tutorial we will reconstruct an MRI image from the sparse kspace
measurments.

Import neuroimaging data
------------------------

We use the toy datasets available in pysap, more specifically a 2D brain slice
and the acquistion cartesian scheme.
We also add some gaussian noise in the image space.
"""

# Package import
import pysap
from pysap.data import get_sample_data
from pysap.plugins.mri.reconstruct.reconstruct import FFT2
from pysap.plugins.mri.low_rank_p_MRI.linear import Wavelet2
from pysap.plugins.mri.parallel_mri.utils import prod_over_maps
from pysap.plugins.mri.parallel_mri.utils import function_over_maps
from pysap.plugins.mri.low_rank_p_MRI.reconstruct import sparse_rec_condatvu
from pysap.plugins.mri.reconstruct.utils import convert_mask_to_locations
from pysap.plugins.mri.low_rank_p_MRI.gradient import Grad2D_pMRI
# from pysap.plugins.mri.parallel_mri.gradient import Grad2D_pMRI_synthesis
from pysap.plugins.mri.parallel_mri.extract_sensitivity_maps import get_Smaps

# Third party import
import numpy as np
import scipy.fftpack as pfft
from scipy.io import loadmat
import matplotlib.pyplot as plt

# Loading input data
image_name = '/home/loubnaelgueddari/Data'\
            '/meas_MID41_CSGRE_ref_OS1_FID14687.mat'
k_space_ref = loadmat(image_name)['ref']
k_space_ref /= np.linalg.norm(k_space_ref)
Smaps, SOS = get_Smaps(k_space_ref, (512, 512), mode='FFT')
mask = get_sample_data("mri-mask")
# mask.show()
image = pysap.Image(data=np.abs(SOS), metadata=mask.metadata)
# image.show()

#############################################################################
# Generate the kspace
# -------------------
#
# From the 2D brain slice and the acquistion mask, we generate the acquisition
# measurments, the observed kspace.
# We then reconstruct the zero order solution.

# Generate the subsampled kspace
Sl = prod_over_maps(Smaps, SOS)
kspace_data = function_over_maps(pfft.fft2, Sl)
kspace_data = prod_over_maps(kspace_data, mask.data)
# mask.show()
kspace_data = []
[kspace_data.append(mask * pfft.fft2(Sl[:, :, channel]))
    for channel in range(Sl.shape[-1])]
kspace_data = np.asarray(kspace_data)
import ipdb; ipdb.set_trace()
# Get the locations of the kspace samples
kspace_loc = convert_mask_to_locations(mask.data)


#############################################################################
# FISTA optimization
# ------------------
#
# We now want to refine the zero order solution using a FISTA optimization.
# Here no cost function is set, and the optimization will reach the
# maximum number of iterations. Fill free to play with this parameter.

# Start the FISTA reconstruction
# import ipdb; ipdb.set_trace()
max_iter = 10

linear_op = Wavelet2(wavelet_name="UndecimatedBiOrthogonalTransform",
                     nb_scale=4)

fourier_op = FFT2(samples=kspace_loc, shape=(512, 512))

gradient_op_cd = Grad2D_pMRI(data=kspace_data,
                             fourier_op=fourier_op)

x_final, transform = sparse_rec_condatvu(
    gradient_op=gradient_op_cd,
    linear_op=linear_op,
    std_est=None,
    mu=1e-7,
    tau=None,
    sigma=None,
    relaxation_factor=1.0,
    nb_of_reweights=0,
    max_nb_of_iter=max_iter,
    add_positivity=False,
    atol=1e-4,
    verbose=1)

image_rec = pysap.Image(data=np.abs(x_final))
image_rec.show()
