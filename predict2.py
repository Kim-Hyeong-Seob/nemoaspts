import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import datetime
from matplotlib import pyplot
import threading

path = '2021-5-5.csv'
voltage = pd.read_csv(path, header=None, index_col=0)
voltage.plot(label="Original", color="orange")
model = ExponentialSmoothing(voltage[2],trend='add',seasonal='add',seasonal_periods=1439).fit()
model.save('ExponentialSmoothing_model.pkl')

class AsyncTask:
    def __init__(self):
        pass

    def Predict(self):
        print ('Predict')
        now = datetime.datetime.now()
        index = now.hour * 60 + now.minute
        pre = model.predict(start=index+1, end=index+1)
        print("Predicted Value",pre.tolist()[0])
        threading.Timer(600,self.Predict).start()
        global pcbsignal
        global sunv
        if pcbsignal == 0 & pre.tolist()[0]<150000:
                GPIO.OUTPUT(15,HIGH) 
        elif pcbsignal != 0 & pre.tolist()[0]>=150000:
                GPIO.OUTPUT(15,LOW)
                



def main():
    at = AsyncTask()
    at.Predict()

if __name__ == '__main__':
    main()

voltage[2].plot(title='nemo')