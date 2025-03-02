# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 08:32:10 2025

@author: rwsmy
"""

#Proposed change to aero_surce.compute_forces_and_moments():
    
    def compute_forces_and_moments(
        self,
        stream_velocity,
        stream_speed,
        stream_mach,
        rho,
        cp,
        *args,
    ):  # pylint: disable=unused-argument
        """Computes the forces and moments acting on the aerodynamic surface.
        Used in each time step of the simulation. This method is valid for
        the barrowman aerodynamic models.
        Parameters
        ----------
        stream_velocity : tuple
            Tuple containing the stream velocity components in the body frame.
        stream_speed : int, float
            Speed of the stream in m/s.
        stream_mach : int, float
            Mach number of the stream.
        rho : int, float
            Density of the stream in kg/m^3.
        cp : Vector
            Center of pressure coordinates in the body frame.
        args : tuple
            Additional arguments.
        Returns
        -------
        tuple of float
            The aerodynamic forces (lift, side_force, drag) and moments
            (pitch, yaw, roll) in the body frame.
        """
        R1, R2, R3, M1, M2, M3 = 0, 0, 0, 0, 0, 0
        cpz = cp[2]
        
        # Account for fin angular position around z-axis (in radians)
        fin_angle_rad = self.fin_angle_rad  # Assuming this property exists or is added
        
        # Get original stream velocity components
        stream_vx, stream_vy, stream_vz = stream_velocity
        
        # Transform velocity components based on fin orientation
        # Rotate velocity vector by negative fin angle to get components in fin's frame
        cos_angle = np.cos(-fin_angle_rad)
        sin_angle = np.sin(-fin_angle_rad)
        fin_stream_vx = stream_vx * cos_angle - stream_vy * sin_angle
        fin_stream_vy = stream_vx * sin_angle + stream_vy * cos_angle
        fin_stream_vz = stream_vz
        
        # Use transformed velocity for angle of attack calculation
        fin_stream_velocity = (fin_stream_vx, fin_stream_vy, fin_stream_vz)
        
        if fin_stream_vx**2 + fin_stream_vy**2 != 0:  # TODO: maybe try/except
            # Normalize component stream velocity in fin frame
            stream_vzn = fin_stream_vz / stream_speed
            if -1 * stream_vzn < 1:
                attack_angle = np.arccos(-stream_vzn)
                c_lift = self.cl.get_value_opt(attack_angle, stream_mach)
                # Component lift force magnitude
                lift = 0.5 * rho * (stream_speed**2) * self.reference_area * c_lift
                
                # Component lift force components in fin frame
                lift_dir_norm = (fin_stream_vx**2 + fin_stream_vy**2) ** 0.5
                fin_lift_x = lift * (fin_stream_vx / lift_dir_norm)
                fin_lift_y = lift * (fin_stream_vy / lift_dir_norm)
                
                # Transform lift force back to body frame
                R1 = fin_lift_x * cos_angle + fin_lift_y * sin_angle
                R2 = -fin_lift_x * sin_angle + fin_lift_y * cos_angle
                R3 = 0
                
                # Calculate moments in body frame
                M1 = -cpz * R2
                M2 = cpz * R1
                M3 = 0  # Roll moment is handled in the fin subclass
                
        return R1, R2, R3, M1, M2, M3