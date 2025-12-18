This file structure was uploaded to EC2 and ran on a t3.micro instance.
The model was created on a JupyterLab instance.
This was created by first storing data found at Kaggle.com in an S3 General Purpose bucket, this data was then accessed
in a SageMaker AI domain using a JupyterLab instance which trained a model (really a dictionary) which mapped products to 
their top 5 recommendations. 
This dictionary was then used in a python flask service so that if you input a product id which is in the dictionary it will output a top 5 products list. 
For some future work the website could look much better and more product ids could be available for use, a sample of the order data had to be taken
so it could not work with all of the data.

In order to run the EC2 Instance, python and other requirements had to be downloaded using the following commands:
sudo yum install python3 python3-pip git -y
mkdir /var/www/html
Then all files where copied over, then requirments.txt was installed with the following command:
pip3 install -r requirements.txt
Then to run the website constantly, gunicorn was installed and configured with app.py

Side note - I followed a youtube tutorial and exported the dictionary as a pkl file, this did not work and needed fixing in the ec2

Directed Link - This is no longer the link to the instance, to save remaining credits it has since been shut down
http://3.236.100.109/
