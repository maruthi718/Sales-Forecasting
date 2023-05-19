from flask import Flask, render_template, request
import numpy as np
import pandas as pd 
import pickle
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# load the model from the file named `model.pickle`
model = pickle.load(open('model.pickle', 'rb'))
            
app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST','GET'])
def predict():
    if request.method=='POST': 
        input_val = request.form['months'] 
        pred_uc = model.get_forecast(steps=int(input_val)) 
        pred_ci = pred_uc.conf_int()
        pred__mean=(pred_ci['lower Sales']+pred_ci['upper Sales'])/2 
        data = np.array(pred__mean) 
        forecast=list(data) 
        import datetime
        current_date = datetime.date.today()
        forecast_index = pd.date_range(start=current_date,periods=int(input_val),freq='MS')   
        data = {'date': forecast_index, 'sales': forecast} 
        df = pd.DataFrame(data) 

        print(df) 
        # plot the scatter plot
        plt.plot(df['date'], df['sales'])


        # set the labels    
        plt.xlabel("Dates")
        plt.ylabel("Sales")
        plt.title("Sales Prediction")

        # Save plot to BytesIO object
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)

        # Convert BytesIO object to base64-encoded string
        plot_url = base64.b64encode(img.getvalue()).decode() 
        #forecast_df = pd.DataFrame(data=forecast,index=forecast_index,columns=['Forecast'])
        
        return render_template('out.html', plot_url=plot_url, df = df)
    elif request.method == 'GET':
        return render_template('index.html')


if __name__=='__main__':
    app.run(debug=True)
    