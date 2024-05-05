import matplotlib.pyplot as plt
import numpy as np
from helpers import ShapeType
from shape import Shape


class Sketch:
    def __init__(self, shape: Shape, light_radius, collection_radius, emission_radius, emission_length, corot_limit):
        self.shape = shape
        
        self.light_radius = light_radius
        self.emission_radius = emission_radius
        self.emission_length = emission_length
        self.collection_radius = collection_radius
        self.corot_limit = corot_limit

        self.theta = np.linspace(0, 2 * np.pi, 100)

    def show_habitat(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        if self.shape.shapeType == ShapeType.Cylinder:
            self.plot_cylinder(ax)
        elif self.shape.shapeType == ShapeType.Tube or self.shape.shapeType == ShapeType.DumbbellTube:
            self.plot_tube(ax)
        elif self.shape.shapeType == ShapeType.Oblate:
            self.plot_oblate(ax)
        elif self.shape.shapeType == ShapeType.Torus:
            self.plot_torus(ax)
        if self.shape.shapeType == ShapeType.Dumbbell or self.shape.shapeType == ShapeType.DumbbellTube:
            self.plot_dumbbell(ax)

        self.draw_electric_ring(ax)

        self.draw_light_paraboloid(ax)

        self.draw_radiator(ax)

    def plot_cylinder(self, ax):
        cylinder_radius = self.shape.rotationalRadius
        # rim:
        z_cylinder = np.linspace(-self.minZ(), self.minZ(), 100)
        theta_cylinder, z_cylinder = np.meshgrid(self.theta, z_cylinder)
        x_cylinder = cylinder_radius * np.cos(theta_cylinder)
        y_cylinder = cylinder_radius * np.sin(theta_cylinder)
        ax.plot_surface(x_cylinder, y_cylinder, z_cylinder, alpha=1, color='green')

        # Plotting the cylinder endcaps
        theta_cap = np.linspace(0, 2 * np.pi, 100)
        cap_radius = np.linspace(0, self.shape.rotationalRadius, 100)
        cap_theta, cap_radius_mesh = np.meshgrid(theta_cap, cap_radius)
        x_cap = cap_radius_mesh * np.cos(cap_theta)
        y_cap = cap_radius_mesh * np.sin(cap_theta)

        # Bottom endcap (always green)
        z_bottom_endcap = -self.shape.cylinderLength / 2 * np.ones_like(x_cap)
        ax.plot_surface(x_cap, y_cap, z_bottom_endcap, color='green', alpha=1)

        # Top endcap
        z_top_endcap = self.shape.cylinderLength / 2 * np.ones_like(x_cap)
        self.draw_habitat_hull(ax, x_cap, y_cap, z_top_endcap)

    def plot_tube(self, ax):
        x_tube = np.linspace(-self.shape.rotationalRadius, self.shape.rotationalRadius, 100)
        theta_tube, x_tube = np.meshgrid(self.theta, x_tube)
        y_tube = self.shape.tubeRadius * np.cos(theta_tube)
        z_tube = self.shape.tubeRadius * np.sin(theta_tube)
        if self.shape.shapeType == ShapeType.Tube:
            mask = x_tube ** 2 + y_tube ** 2 <= self.shape.rotationalRadius ** 2
        else:
            x_hab = self.shape.rotationalRadius - self.shape.dumbbellMinorRadius
            x_opp = -self.shape.oppositeRotationalRadius + self.shape.dumbbellMajorRadius
            mask = np.logical_and(np.logical_and((x_tube - x_hab) ** 2 + y_tube ** 2 > self.shape.dumbbellMinorRadius ** 2,
                                (x_tube - x_opp) ** 2 + y_tube ** 2 > self.shape.dumbbellMajorRadius ** 2),
                                x_tube > x_opp)
        x, y, z = np.where(mask, x_tube, np.nan), np.where(mask, y_tube, np.nan), np.where(mask, z_tube, np.nan)
        self.draw_habitat_hull(ax, x, y, z)

        if self.shape.shapeType == ShapeType.Tube:
            # Plotting the endcaps
            z_cylinder = np.linspace(-self.shape.tubeRadius, self.shape.tubeRadius, 100)
            theta_cylinder, z_cylinder = np.meshgrid(self.theta, z_cylinder)
            x_cylinder = self.shape.rotationalRadius * np.cos(theta_cylinder)
            y_cylinder = self.shape.rotationalRadius * np.sin(theta_cylinder)

            # Mask for the part of the cylinder less than self.shape.tubeRadius from the x-axis
            mask = y_cylinder ** 2 + z_cylinder ** 2 <= self.shape.tubeRadius ** 2

            # Apply the mask
            x_cylinder_masked = np.where(mask, x_cylinder, np.nan)  # Mask out-of-bound values with NaN
            y_cylinder_masked = np.where(mask, y_cylinder, np.nan)
            z_cylinder_masked = np.where(mask, z_cylinder, np.nan)

            # Only plot the parts of the disk inside the cylinder's radius
            ax.plot_surface(x_cylinder_masked, y_cylinder_masked, z_cylinder_masked, alpha=1, color='green')

    def plot_oblate(self, ax):
        phi = np.linspace(0, 2 * np.pi, 100)
        theta = np.linspace(0, np.pi, 100)
        phi, theta = np.meshgrid(phi, theta)
        x = self.shape.rotationalRadius * np.sin(theta) * np.cos(phi)
        y = self.shape.rotationalRadius * np.sin(theta) * np.sin(phi)
        z = self.shape.oblateRadius * np.cos(theta)
        self.draw_habitat_hull(ax, x, y, z)

    def plot_torus(self, ax):
        # Define the angles
        theta = np.linspace(0, 2 * np.pi, 100)
        phi = np.linspace(0, 2 * np.pi, 100)
        theta, phi = np.meshgrid(theta, phi)

        R = self.shape.rotationalRadius - self.shape.torusHabRadius  # Distance from the center of the tube to the center of the torus
        # Parametric equations for the torus
        x = (R + self.shape.torusHabRadius * np.cos(phi)) * np.cos(theta)
        y = (R + self.shape.torusHabRadius * np.cos(phi)) * np.sin(theta)
        z = self.shape.torusHabRadius * np.sin(phi)
        self.draw_habitat_hull(ax, x, y, z)

    def plot_dumbbell(self, ax):
        phi = np.linspace(0, 2 * np.pi, 100)
        theta = np.linspace(0, np.pi, 100)
        phi, theta = np.meshgrid(phi, theta)
        x = self.shape.dumbbellMinorRadius * np.sin(theta) * np.cos(phi) + self.shape.rotationalRadius - self.shape.dumbbellMinorRadius
        y = self.shape.dumbbellMinorRadius * np.sin(theta) * np.sin(phi)
        z = self.shape.dumbbellMinorRadius * np.cos(theta)
        self.draw_habitat_hull(ax, x, y, z)

        x = self.shape.dumbbellMajorRadius * np.sin(theta) * np.cos(phi) - self.shape.oppositeRotationalRadius + self.shape.dumbbellMajorRadius
        y = self.shape.dumbbellMajorRadius * np.sin(theta) * np.sin(phi)
        z = self.shape.dumbbellMajorRadius * np.cos(theta)
        self.draw_habitat_hull(ax, x, y, z)

        ax.plot([self.shape.rotationalRadius - 2 * self.shape.dumbbellMinorRadius,  - self.shape.oppositeRotationalRadius + 2 * self.shape.dumbbellMajorRadius], [0, 0], [0, 0], color='black')

    def draw_habitat_hull(self, ax, xHab, yHab, zHab):
        mask_light = np.logical_and(xHab ** 2 + yHab ** 2 < self.light_radius ** 2, zHab > 0)
        x = np.where(mask_light, xHab, np.nan)
        y = np.where(mask_light, yHab, np.nan)
        z = np.where(mask_light, zHab, np.nan)
        ax.plot_surface(x, y, z, color='yellow', alpha=1)

        mask_electric = np.logical_and((self.light_radius ** 2 < xHab ** 2 + yHab ** 2)
                              & (xHab ** 2 + yHab ** 2 < self.collection_radius ** 2), zHab > 0)
        x = np.where(mask_electric, xHab, np.nan)
        y = np.where(mask_electric, yHab, np.nan)
        z = np.where(mask_electric, zHab, np.nan)
        ax.plot_surface(x, y, z, color='blue', alpha=1)

        mask_habitat = ~(mask_light | mask_electric)
        x = np.where(mask_habitat, xHab, np.nan)
        y = np.where(mask_habitat, yHab, np.nan)
        z = np.where(mask_habitat, zHab, np.nan)
        ax.plot_surface(x, y, z, color='green', alpha=1)

    def draw_light_paraboloid(self, ax):

        paraboloid_height = self.light_radius / 2

        # z values span from the bottom to the top of the paraboloid
        z_paraboloid = np.linspace(-paraboloid_height, 0, 100)

        # Create a meshgrid for theta and z
        theta_paraboloid, z_paraboloid = np.meshgrid(self.theta, z_paraboloid)

        # The radius at each height z, following the paraboloid's equation
        # Since z = k * r^2 - paraboloid_height,  solving for r gives r = sqrt((z+paraboloid_height)/k),
        # and k = paraboloid_height / light_radius^2 at z=0
        k = paraboloid_height / (self.light_radius ** 2)
        r_paraboloid = np.sqrt((z_paraboloid + paraboloid_height) / k)

        # Now, calculate the x and y coordinates
        x_paraboloid = r_paraboloid * np.cos(theta_paraboloid)
        y_paraboloid = r_paraboloid * np.sin(theta_paraboloid)

        mask = self.maskXY_habitat(x_paraboloid, y_paraboloid)
        x = np.where(mask, x_paraboloid, np.nan)
        y = np.where(mask, y_paraboloid, np.nan)
        z = np.where(mask, z_paraboloid, np.nan)
        ax.plot_surface(x, y, z, color='yellow', alpha=.5)

    def draw_electric_ring(self, ax):
        ring_radius = np.linspace(self.light_radius, self.collection_radius, 100)
        theta_ring, ring_radius = np.meshgrid(self.theta, ring_radius)
        x_ring = ring_radius * np.cos(theta_ring)
        y_ring = ring_radius * np.sin(theta_ring)
        z_ring = np.zeros_like(x_ring)  # Ensure z_ring has the same shape as x_ring and y_ring

        mask = self.maskXY_habitat(x_ring, y_ring)
        x = np.where(mask, x_ring, np.nan)
        y = np.where(mask, y_ring, np.nan)
        z = np.where(mask, z_ring, np.nan)
        ax.plot_surface(x, y, z, color='blue', alpha=.8)

    def draw_radiator(self, ax):
        minZ = self.minZ()
        # Plotting the axis as a red line
        ax.plot([0, 0], [0, 0], [-self.minZ() - self.emission_length, self.minZ() + self.emission_length], color='red')
        # Plotting the cricitcal co-rotational radius
        x_ring = self.corot_limit * np.cos(self.theta)
        y_ring = self.corot_limit * np.sin(self.theta)
        z_ring = np.zeros_like(self.theta)  # Ring lies in the XY plane, so z is zero
        ax.plot(x_ring, y_ring, z_ring, linestyle='--', color='red')

        # Plotting the planes
        x_plane = np.linspace(-self.emission_radius, self.emission_radius, 2)
        z_plane_lower = np.linspace(-self.minZ(), -self.minZ() - self.emission_length, 2)
        z_plane_upper = np.linspace(self.minZ(), self.minZ() + self.emission_length, 2)

        # Plane on one side of the cylinder
        X_plane, Z_plane_lower = np.meshgrid(x_plane, z_plane_lower)
        X_plane, Z_plane_upper = np.meshgrid(x_plane, z_plane_upper)
        Y_plane_lower = np.full(X_plane.shape, 0)
        Y_plane_upper = np.full(X_plane.shape, 0)

        ax.plot_surface(X_plane, Y_plane_lower, Z_plane_lower, alpha=.8, color='darkgrey')
        ax.plot_surface(X_plane, Y_plane_upper, Z_plane_upper, alpha=.8, color='darkgrey')

        # Determine the maximum range for the axes
        max_range = max(self.minZ() + self.emission_length, self.collection_radius, self.shape.rotationalRadius)

        # Set the same scale for all axes
        ax.set_xlim(-max_range, max_range)
        ax.set_ylim(-max_range, max_range)
        ax.set_zlim(-max_range, max_range)

        # Setting the labels with units [m]
        ax.set_xlabel('X axis [m]')
        ax.set_ylabel('Y axis [m]')
        ax.set_zlabel('Z axis (to Sun) [m]')

    def maskXY_habitat(self, x, y):
        if self.shape.shapeType == ShapeType.Cylinder or self.shape.shapeType == ShapeType.Oblate:
            return x ** 2 + y ** 2 > self.shape.rotationalRadius ** 2
        elif self.shape.shapeType == ShapeType.Tube:
            return np.logical_or(x ** 2 + y ** 2 > self.shape.rotationalRadius ** 2,
                                 abs(y) > self.shape.tubeRadius)
        elif self.shape.shapeType == ShapeType.Torus:
            return np.logical_or(x ** 2 + y ** 2 > self.shape.rotationalRadius ** 2,
                                 x ** 2 + y ** 2 < (self.shape.rotationalRadius - 2 * self.shape.torusHabRadius) ** 2)
        elif self.shape.shapeType == ShapeType.Dumbbell:
            x_hab = self.shape.rotationalRadius - self.shape.dumbbellMinorRadius
            x_opp = -self.shape.oppositeRotationalRadius + self.shape.dumbbellMajorRadius
            return np.logical_and((x - x_hab) ** 2 + y ** 2 > self.shape.dumbbellMinorRadius ** 2,
                                  (x - x_opp) ** 2 + y ** 2 > self.shape.dumbbellMajorRadius ** 2)
        elif self.shape.shapeType == ShapeType.DumbbellTube:
            x_hab = self.shape.rotationalRadius - self.shape.dumbbellMinorRadius
            x_opp = -self.shape.oppositeRotationalRadius + self.shape.dumbbellMajorRadius
            return np.logical_and(
                np.logical_and((x - x_hab) ** 2 + y ** 2 > self.shape.dumbbellMinorRadius ** 2,
                                (x - x_opp) ** 2 + y ** 2 > self.shape.dumbbellMajorRadius ** 2),
                np.logical_or(np.logical_or(x > self.shape.rotationalRadius,  x < -self.shape.oppositeRotationalRadius),
                              abs(y) > self.shape.tubeRadius))

    def minZ(self):
        if self.shape.shapeType == ShapeType.Cylinder:
            return self.shape.cylinderLength / 2
        elif self.shape.shapeType == ShapeType.Tube:
            return self.shape.tubeRadius
        elif self.shape.shapeType == ShapeType.Oblate:
            return self.shape.oblateRadius
        elif self.shape.shapeType == ShapeType.Torus:
            return self.shape.torusHabRadius
        elif self.shape.shapeType == ShapeType.Dumbbell:
            return max(self.shape.dumbbellMinorRadius, self.shape.dumbbellMajorRadius)
        elif self.shape.shapeType == ShapeType.DumbbellTube:
            return max(self.shape.dumbbellMinorRadius, self.shape.dumbbellMajorRadius, self.shape.tubeRadius)


if __name__ == '__main__':
    class ShapeMock:
        shapeType = ShapeType.Dumbbell
        rotationalRadius = 1
        oppositeRotationalRadius = 0.5
        cylinderLength = 1.3
        tubeRadius = 0.5
        oblateRadius = 0.5
        torusHabRadius = 0.2
        dumbbellMinorRadius = 0.2
        dumbbellMajorRadius = dumbbellMinorRadius * 2 ** (1/3)

    sketch = Sketch(shape=ShapeMock(), light_radius=.8, collection_radius=.9, emission_radius=.6, emission_length=1.2, corot_limit=1.3)
    sketch.show_habitat()
    plt.show()
