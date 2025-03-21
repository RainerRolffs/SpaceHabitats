from input import Input
from structure import Structure
import matplotlib.pyplot as plt

class DisplayStructuralFraction:
    def __init__(self):
        self.inp = Input()
        self.inp.distanceBetweenVerticalCables = 50

        struc = Structure(self.inp, rotationalRadius=100)

        N = 1000
        xvals = [i/N * 1.5 for i in range(N)]  # fractions of co-rot. radius
        vert = [struc.ComputeVerticalStructuralFraction(radius=xvals[i] * struc.coRotationalRadius,
                                                        withBridges=False) for i in range(N)]
        vertBridges = [struc.ComputeVerticalStructuralFraction(radius=xvals[i] * struc.coRotationalRadius,
                                                        withBridges=True) for i in range(N)]
        hor = [struc.ComputeHorizontalStructuralFraction(radius= xvals[i] * struc.coRotationalRadius) for i in range(N)]
        noself = [struc.ComputeStructuralFractionWithoutSelfWeight(radius= xvals[i] * struc.coRotationalRadius) for i in range(N)]

        fig, ax = plt.subplots()
        ax.set_title("Structural mass fraction")
        ax.set_xlabel("Ratio of radius to critical co-rotational radius")
        ax.set_ylabel("Ratio of structural mass to supported mass")
#        ax.semilogy()

        ax.set_ylim(0, 2)

        ax.plot(xvals, vert, label="Vertical",
                linestyle="-", color="green")
        ax.plot(xvals, vertBridges, label="Vertical with Bridges", linestyle="-",
                color="red")
        ax.plot(xvals, hor, label="Horizontal",
                linestyle="-", color="blue")
        ax.plot(xvals, noself, label="No Self-Weight", linestyle="-", color="black")
        plt.subplots_adjust(right=0.75)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

        plt.show()


if __name__ == '__main__':
    DisplayStructuralFraction()
