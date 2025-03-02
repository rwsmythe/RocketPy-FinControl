# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 08:43:09 2025

@author: rwsmy
"""

#proposed changes for fins.py
def evaluate_roll_parameters(self):
    """Calculates and returns an individual fin's roll coefficients.
    The roll coefficients are saved in a list.
    Returns
    -------
    self.roll_parameters : list
        List containing the roll moment lift coefficient, the
        roll moment damping coefficient and the cant angle in
        radians
    """
    self.cant_angle_rad = np.radians(self.cant_angle)
    
    # For a single fin, self.n should be 1
    # Removing the n factor as it's now implicitly 1
    clf_delta = (
        self.roll_forcing_interference_factor
        * (self.Yma + self.rocket_radius)
        * self.clalpha_single_fin
        / self.d
    )  # Function of mach number
    clf_delta.set_inputs("Mach")
    clf_delta.set_outputs("Roll moment forcing coefficient derivative")
    
    cld_omega = (
        2
        * self.roll_damping_interference_factor
        * self.clalpha_single_fin
        * np.cos(self.cant_angle_rad)
        * self.roll_geometrical_constant
        / (self.ref_area * self.d**2)
    )  # Function of mach number
    cld_omega.set_inputs("Mach")
    cld_omega.set_outputs("Roll moment damping coefficient derivative")
    
    self.roll_parameters = [clf_delta, cld_omega, self.cant_angle_rad]
    return self.roll_parameters

def compute_forces_and_moments(
        self,
        stream_velocity,
        stream_speed,
        stream_mach,
        rho,
        cp,
        omega,
        *args,
    ):  # pylint: disable=arguments-differ
        """Computes the forces and moments acting on an individual fin.
        Parameters
        ----------
        stream_velocity : tuple of float
            The velocity of the airflow relative to the surface.
        stream_speed : float
            The magnitude of the airflow speed.
        rho : float
            Air density.
        cp : Vector
            Center of pressure coordinates in the body frame.
        omega: tuple[float, float, float]
            Tuple containing angular velocities around the x, y, z axes.
        Returns
        -------
        tuple of float
            The aerodynamic forces (lift, side_force, drag) and moments
            (pitch, yaw, roll) in the body frame for this individual fin.
        """
        # Get forces and moments from parent class calculation (non-roll effects)
        R1, R2, R3, M1, M2, _ = super().compute_forces_and_moments(
            stream_velocity,
            stream_speed,
            stream_mach,
            rho,
            cp,
        )
        
        # Get this individual fin's roll parameters
        clf_delta, cld_omega, cant_angle_rad = self.roll_parameters
        
        # Calculate roll moment due to fin cant (forcing component)
        M3_forcing = (
            (1 / 2 * rho * stream_speed**2)
            * self.reference_area
            * self.reference_length
            * clf_delta.get_value_opt(stream_mach)
            * cant_angle_rad  # Using this specific fin's cant angle
        )
        
        # Calculate roll damping moment for this individual fin
        M3_damping = (
            (1 / 2 * rho * stream_speed)
            * self.reference_area
            * (self.reference_length) ** 2
            * cld_omega.get_value_opt(stream_mach)
            * omega[2]
            / 2  # Assuming this factor is already accounting for individual fin contribution
        )
        
        # Total roll moment for this fin
        M3 = M3_forcing - M3_damping
        
        return R1, R2, R3, M1, M2, M3