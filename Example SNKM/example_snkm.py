import numpy as np
from sympy import *
from pydsge import DSGE
import matplotlib.pyplot as plt


# ================================
# ===== MODEL ESPECIFICATION =====
# ================================
# endogenous variables at t
y, pi, i, a, v, exp_y, exp_pi = symbols('y, pi, i, a, v, exp_y, exp_pi')

endog = Matrix([y, pi, i, a, v, exp_y, exp_pi])

# endogenous variables at t - 1
yl, pil, il, al, vl, exp_yl, exp_pil = symbols('yl, pil, il, al, vl, exp_yl, exp_pil')

endogl = Matrix([yl, pil, il, al, vl, exp_yl, exp_pil])

# exogenous shocks
eps_a, eps_v, eps_pi = symbols('eps_a, eps_v, eps_pi')

exog = Matrix([eps_a, eps_v, eps_pi])

# expectational shocks
eta_y, eta_pi = symbols('eta_y, eta_pi')

expec = Matrix([eta_y, eta_pi])

# parameters
sigma, varphi, alpha, beta, theta, phi_pi, phi_y, rho_a, sigma_a, rho_v, sigma_v, sigma_pi = \
    symbols('sigma, varphi, alpha, beta, theta, phi_pi, phi_y, rho_a, sigma_a, rho_v, sigma_v, sigma_pi')

estimate_param = Matrix([sigma, theta, phi_pi, phi_y, rho_a, sigma_a, rho_v, sigma_v, sigma_pi])
calib_param = {varphi: 1, alpha:0.4, beta: 0.997805}

# Summary parameters
psi_nya = (1 + varphi) / (sigma*(1-alpha) + varphi + alpha)
kappa = (1 - theta)*(1 - theta * beta)*(sigma*(1-alpha) + varphi + alpha)

# model equations
eq1 = y - exp_y + (1/sigma)*(i - exp_pi) - psi_nya * (rho_a - 1) * a
eq2 = pi - beta * exp_pi - kappa * y - sigma_pi * eps_pi
eq3 = i - phi_pi * pi - phi_y * y - v
eq4 = a - rho_a * al - sigma_a * eps_a
eq5 = v - rho_v * vl - sigma_v * eps_v
eq6 = y - exp_yl - eta_y
eq7 = pi - exp_pil - eta_pi

equations = Matrix([eq1, eq2, eq3, eq4, eq5, eq6, eq7])


# ======================
# ===== SIMULATION =====
# ======================

calib_dict = {sigma: 1.3,
              varphi: 1,
              alpha: 0.4,
              beta: 0.997805,
              theta: 0.75,
              phi_pi: 1.5,
              phi_y: 0.2,
              rho_a: 0.9,
              sigma_a: 1.1,
              rho_v: 0.5,
              sigma_v: 0.3,
              sigma_pi: 0.8}

obs_matrix = Matrix(np.zeros((3, 7)))
obs_matrix[0, 0] = 1
obs_matrix[1, 1] = 1
obs_matrix[2, 2] = 1

obs_offset = Matrix(np.zeros(3))

dsge_simul = DSGE(endog, endogl, exog, expec, equations,
                  calib_dict=calib_dict,
                  obs_matrix=obs_matrix,
                  obs_offset=obs_offset)
print(dsge_simul.eu)

df_obs, df_states = dsge_simul.simulate(n_obs=250, random_seed=1)

df_states = df_states.tail(200)
df_obs = df_obs.tail(200)

# df_obs.plot()
# plt.show()


# =============================
# ===== MODEL ESTIMATION  =====
# =============================

# TODO change prior table to choose mean and std
# priors
prior_dict = {sigma:    {'dist': 'normal',   'param a':  1.3, 'param b': 0.20},
              theta:    {'dist': 'beta',     'param a':  3.0, 'param b': 2.00},
              phi_pi:   {'dist': 'normal',   'param a':  1.5, 'param b': 0.35},
              phi_y:    {'dist': 'gamma',    'param a':  6.2, 'param b': 0.04},
              rho_a:    {'dist': 'beta',     'param a':  1.5, 'param b': 1.50},
              sigma_a:  {'dist': 'invgamma', 'param a':  6.0, 'param b': 2.50},
              rho_v:    {'dist': 'beta',     'param a':  1.5, 'param b': 1.50},
              sigma_v:  {'dist': 'invgamma', 'param a':  6.0, 'param b': 2.50},
              sigma_pi: {'dist': 'invgamma', 'param a':  6.0, 'param b': 2.50}}


dsge = DSGE(endog, endogl, exog, expec, equations,
            estimate_params=estimate_param,
            calib_dict=calib_param,
            obs_matrix=obs_matrix,
            obs_offset=obs_offset,
            prior_dict=prior_dict,
            obs_data=df_obs)

df_chains, accepted = dsge.estimate(nsim=1000, ck=0.2, file_path='snkm.h5')
print(accepted)
df_chains.plot()
plt.show()

df_chains.astype(float).hist(bins=50)
plt.show()
