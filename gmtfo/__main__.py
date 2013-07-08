from sys import argv
from gmtfo.app import app

app.run(debug="-d" in argv)
