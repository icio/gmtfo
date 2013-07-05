from sys import argv
from gmtfo import app

app.run(debug="-d" in argv)
