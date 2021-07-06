""" Spread of Covid -19 Inspired Article : https://www.washingtonpost.com/graphics/2020/health/coronavirus-how-epidemics-spread-and-end/ """

import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.animation as ani 

covidParams = {
    "r0": 2.28,
    "incubation": 5,
    "percent_mild": 0.8,
    "mild_recovery": (7, 14),
    "percent_severe": 0.2,
    "severe_recovery": (21, 42),
    "severe_death": (14, 56),
    "fatality_rate": 0.034,
    "serial_interval": 7
}

class virus() : 

    def __init__(self, params) : 
        self.fig = plt.figure() 
        self.axes = self.fig.add_subplot( projection = "polar")
        self.axes.grid(False)
        self.axes.set_xticklabels([])
        self.axes.set_yticklabels([])
        self.axes.set_ylim(0, 1) 


        self.dayText = self.axes.annotate("day 0", xy = [np.pi / 2, 1], ha = 'center', va = 'bottom', color = 'black')
        self.infectedText = self.axes.annotate("infected 0", xy = [3*np.pi/2, 1], ha = "center", va = "top", color = 'red')
        self.recoveredText = self.axes.annotate("\nrecovered 0" , xy = [3*np.pi/2, 1 ], ha = "center", va = "top", color = "blue")
        self.deadText = self.axes.annotate("\n\n dead 0", xy = [3*np.pi/2, 1], ha = 'center' , va = 'top', color ='black') 


        self.day = 0
        self.totalInfected = 0
        self.currentlyInfected = 0
        self.numRecovered = 0
        self.numDeaths = 0
        self.r0 = covidParams["r0"]
        self.percentMild = covidParams["percent_mild"]
        self.percentSevere = covidParams["percent_severe"]
        self.fatalityRate = covidParams["fatality_rate"]
        self.serialInterval = covidParams["serial_interval"]

        self.mildFast = covidParams['incubation'] + covidParams['mild_recovery'][0]
        self.mildSlow = covidParams['incubation'] + covidParams['mild_recovery'][1]
        self.severeFast = covidParams['incubation'] + covidParams['severe_recovery'][0]
        self.severeSlow = covidParams['incubation'] + covidParams['severe_recovery'][1]
        self.deathFast = covidParams['incubation'] + covidParams['severe_death'][0]
        self.deathSlow = covidParams['incubation'] + covidParams['severe_death'][1]

        self.mild = {i : {"thetas" : [] , "rs" : []} for i in range(self.mildFast, 366)}
        self.severe = { 
            "recovery" : {i : {'thetas' : [], "rs" : []} for i in range(self.severeFast, 366)},
            "death" : {i : {'thetas' : [], 'rs' :[]} for i in range(self.deathFast, 366)}                        
        }

        self.exposedBefore = 0 
        self.exposedAfter = 1 

        self.initialPopulation()


    def initialPopulation(self) : 
        population = 4500
        self.currentlyInfected = 1
        self.totalInfected = 1
        indices = np.arange(0, population) + 0.5
        self.thetas = np.pi * (1 + 5**0.5) * indices 
        self.rs = np.sqrt(indices / population)
        self.plot = self.axes.scatter(self.thetas, self.rs, s=5, color= 'grey')
        self.axes.scatter(self.thetas[0],self.rs[0], s= 5, color = 'red')
        self.mild[self.mildFast]["thetas"].append(self.thetas[0])
        self.mild[self.mildFast]["rs"].append(self.rs[0])

    def spreadVirus(self, i) : 
        self.exposedBefore = self.exposedAfter 
        if self.day % self.serialInterval == 0 and self.exposedBefore < 4500 :
            self.newInfected = round(self.r0 * self.totalInfected)
            self.exposedAfter += round(self.newInfected * 1.1)
            if self.exposedAfter > 4500 : 
                self.newInfected = round((4500 - self.exposedBefore) * 0.9)
                self.exposedAfter = 4500 
            self.currentlyInfected += self.newInfected 
            self.totalInfected += self.newInfected
            self.newInfectedIndices = list(
                np.random.choice(
                    range(self.exposedBefore,self.exposedAfter),
                    self.newInfected,replace = False
                )
            )

            thetas = [self.thetas[i] for i in self.newInfectedIndices]
            rs = [self.rs[i] for i in self.newInfectedIndices]

            self.anim.event_source.stop() 
            if len(self.newInfectedIndices) > 24 : 
                sizeList = round(len(self.newInfectedIndices) / 24)
                thetaChunks = list(self.chunks(thetas, sizeList))
                rChunks = list(self.chunks(rs, sizeList))

                self.anim2 = ani.FuncAnimation(
                    self.fig, 
                    self.oneByOne,
                    interval = 50, 
                    frames = len(thetaChunks),
                    fargs = (thetaChunks, rChunks,'red')
                )

            else : 
                self.anim2 = ani.FuncAnimation(
                    self.fig, 
                    self.oneByOne, interval = 50, 
                    frames = len(thetas), 
                    fargs = (thetas , rs , 'red')
                )
            self.asssignSymptoms()

        self.day+=1 
        self.updateStatus()
        self.updateText()

    def oneByOne(self, i , thetas ,rs, color) : 
        self.axes.scatter(thetas[i], rs[i], s = 5 , color = color )
        if i == (len(thetas) - 1) : 
            self.anim2.event_source.stop() 
            self.anim.event_source.start()

    def chunks(self, aList , n) : 
        for i in range(0, len(aList), n) : 
            yield aList[i : i+n]

    def asssignSymptoms(self) : 
        numMild = round(self.percentMild * self.newInfected)
        numSevere = round(self.percentSevere * self.newInfected)

        self.mildIndices = np.random.choice(self.newInfectedIndices, numMild, replace = False)

        remainingIndices = [i for i in self.newInfectedIndices if i not in self.mildIndices]
        percentSevereRecovery = 1 - (self.fatalityRate / self.percentSevere)
        numSevereRecovery = round(percentSevereRecovery * numSevere)

        self.severeIndices = [] 
        self.deathIndices = [] 

        if remainingIndices : 
            self.severeIndices = np.random.choice(remainingIndices, numSevereRecovery, replace = False)
            self.deathIndices = [i for i in remainingIndices if i not in self.severeIndices]

        low = self.day + self.mildFast 
        high = self.day + self.mildSlow 

        for m in self.mildIndices : 
            recoveryDay = np.random.randint(low, high)
            mildTheta = self.thetas[m]
            mildR = self.rs[m]
            self.mild[recoveryDay]['thetas'].append(mildTheta)
            self.mild[recoveryDay]['rs'].append(mildR)
        
        low = self.day + self.severeFast 
        high = self.day + self.severeSlow

        for recovery in self.severeIndices : 
            recoveryDay = np.random.randint(low, high)
            recoveryTheta = self.thetas[recovery]
            recoveryR = self.rs[recovery]
            self.severe['recovery'][recoveryDay]['thetas'].append(recoveryTheta)
            self.severe['recovery'][recoveryDay]['rs'].append(recoveryR)

        low = self.day + self.deathFast 
        high = self.day + self.deathSlow 

        for death in self.deathIndices : 
            deathDay = np.random.randint(low, high)
            deadTheta = self.thetas[death]
            deadR = self.rs[death]

            self.severe['death'][deathDay]['thetas'].append(deadTheta)
            self.severe['death'][deathDay]['rs'].append(deadR)

    def updateStatus(self):
        if self.day >= self.mildFast : 
            mildThetas = self.mild[self.day]['thetas']
            mildRs = self.mild[self.day]['rs']
            self.axes.scatter(mildThetas, mildRs, s = 5, color = 'green')
            self.numRecovered += len(mildThetas)
            self.currentlyInfected -= len(mildThetas)

        if self.day >= self.severeFast : 
            recThetas = self.severe['recovery'][self.day]['thetas']
            recRs = self.severe['recovery'][self.day]['rs']

            self.axes.scatter(recThetas,recRs, s = 5 , color = 'green')
            self.numRecovered+=len(recThetas)
            self.currentlyInfected-=len(recThetas)

        if self.day >= self.deathFast : 
            deathThetas = self.severe['death'][self.day]['thetas']
            deathRs = self.severe['death'][self.day]['rs']

            self.axes.scatter(deathThetas,deathRs, s = 5 , color = 'black')
            self.numDeaths += len(deathThetas)
            self.currentlyInfected -= len(deathThetas)

    def updateText(self):
        self.dayText.set_text("Day {}".format(self.day))
        self.infectedText.set_text("Infected: {}".format(self.currentlyInfected))
        self.deadText.set_text("\nDeaths: {}".format(self.numDeaths))
        self.recoveredText.set_text("\n\nRecovered: {}".format(self.numRecovered))


    def gen(self):
        while self.numDeaths + self.numRecovered < self.totalInfected:
            yield


    def animate(self):
        self.anim = ani.FuncAnimation(
            self.fig,
            self.spreadVirus,
            frames=self.gen,
            repeat=True)

def main() : 
    cVirus = virus(covidParams)
    cVirus.animate() 
    plt.show() 

if __name__ == "__main__" : 
    main() 
