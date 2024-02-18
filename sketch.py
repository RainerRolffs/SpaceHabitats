import matplotlib.pyplot as plt
import numpy as np


class Sketch:
    def __init__(self, rotational_radius, cylinder_length_to_rot_radius, light_radius, collection_radius, emission_radius, emission_length):
        self.rotational_radius = rotational_radius
        self.cylinder_length = rotational_radius * cylinder_length_to_rot_radius
        self.light_radius = light_radius
        self.emission_radius = emission_radius
        self.emission_length = emission_length
        self.collection_radius = collection_radius

    def plot_shape(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plotting the cylinder
        cylinder_height = self.cylinder_length
        cylinder_radius = self.rotational_radius
        theta = np.linspace(0, 2*np.pi, 100)
        z_cylinder = np.linspace(-cylinder_height/2, cylinder_height/2, 100)
        theta_cylinder, z_cylinder = np.meshgrid(theta, z_cylinder)
        x_cylinder = cylinder_radius * np.cos(theta_cylinder)
        y_cylinder = cylinder_radius * np.sin(theta_cylinder)
        ax.plot_surface(x_cylinder, y_cylinder, z_cylinder, alpha=1, color='green')

        # Plotting the cylinder endcaps
        theta_cap = np.linspace(0, 2 * np.pi, 100)
        cap_radius = np.linspace(0, self.rotational_radius, 100)
        cap_theta, cap_radius_mesh = np.meshgrid(theta_cap, cap_radius)
        x_cap = cap_radius_mesh * np.cos(cap_theta)
        y_cap = cap_radius_mesh * np.sin(cap_theta)

        # Bottom endcap (always green)
        z_bottom_endcap = -cylinder_height / 2 * np.ones_like(x_cap)
        ax.plot_surface(x_cap, y_cap, z_bottom_endcap, color='green', alpha=1)

        # Top endcap
        z_top_endcap = cylinder_height / 2 * np.ones_like(x_cap)

        if self.light_radius < self.rotational_radius:
            # Create a masked area for the yellow part
            mask_yellow = cap_radius_mesh <= self.light_radius
            x_yellow = np.where(mask_yellow, x_cap, np.nan)
            y_yellow = np.where(mask_yellow, y_cap, np.nan)
            z_yellow = np.where(mask_yellow, z_top_endcap, np.nan)
            ax.plot_surface(x_yellow, y_yellow, z_yellow, color='yellow', alpha=1)

            # Create a masked area for the blue part
            mask_green = cap_radius_mesh > self.light_radius
            x_green = np.where(mask_green, x_cap, np.nan)
            y_green = np.where(mask_green, y_cap, np.nan)
            z_green = np.where(mask_green, z_top_endcap, np.nan)
            ax.plot_surface(x_green, y_green, z_green, color='blue', alpha=1)
        else:
            # If lightRadius >= rotationalRadius, plot the entire top endcap in yellow
            ax.plot_surface(x_cap, y_cap, z_top_endcap, color='yellow', alpha=1)

        # Plotting the ring
        ring_radius = np.linspace(max(self.light_radius, self.rotational_radius), self.collection_radius, 100)
        theta_ring, ring_radius = np.meshgrid(theta, ring_radius)
        x_ring = ring_radius * np.cos(theta_ring)
        y_ring = ring_radius * np.sin(theta_ring)
        z_ring = np.zeros_like(x_ring)  # Ensure z_ring has the same shape as x_ring and y_ring
        ax.plot_surface(x_ring, y_ring, z_ring, alpha=.8, color='blue')

        if self.light_radius > self.rotational_radius:
            # Plotting the cone
            cone_height = self.light_radius - self.rotational_radius
            z_cone = np.linspace(-cone_height/2, cone_height/2, 100)
            cone_theta, z_cone = np.meshgrid(theta, z_cone)
            cone_radius = np.linspace(self.rotational_radius, self.light_radius, 100)[:, None]
            x_cone = cone_radius * np.cos(cone_theta)
            y_cone = cone_radius * np.sin(cone_theta)
            ax.plot_surface(x_cone, y_cone, z_cone, alpha=.8, color='yellow')

        # Plotting the axis as a red line
        ax.plot([0, 0], [0, 0], [-cylinder_height/2 - self.emission_length, cylinder_height/2 + self.emission_length], color='red')

        # Plotting the planes
        x_plane = np.linspace(-self.emission_radius, self.emission_radius, 2)
        z_plane_lower = np.linspace(-cylinder_height/2, -cylinder_height/2 - self.emission_length, 2)
        z_plane_upper = np.linspace(cylinder_height/2, cylinder_height/2 + self.emission_length, 2)

        # Plane on one side of the cylinder
        X_plane, Z_plane_lower = np.meshgrid(x_plane, z_plane_lower)
        X_plane, Z_plane_upper = np.meshgrid(x_plane, z_plane_upper)
        Y_plane_lower = np.full(X_plane.shape, 0)
        Y_plane_upper = np.full(X_plane.shape, 0)

        ax.plot_surface(X_plane, Y_plane_lower, Z_plane_lower, alpha=.8, color='darkgrey')
        ax.plot_surface(X_plane, Y_plane_upper, Z_plane_upper, alpha=.8, color='darkgrey')

        # Determine the maximum range for the axes
        max_range = max(cylinder_height / 2 + self.emission_length, self.collection_radius)

        # Set the same scale for all axes
        ax.set_xlim(-max_range, max_range)
        ax.set_ylim(-max_range, max_range)
        ax.set_zlim(-max_range, max_range)

        # Setting the labels with units [m]
        ax.set_xlabel('X axis [m]')
        ax.set_ylabel('Y axis [m]')
        ax.set_zlabel('Z axis (to Sun) [m]')


if __name__ == '__main__':
    sketch = Sketch(4, 1.3, 7, 10, 6, 12)
    sketch.plot_shape()
    plt.show()
