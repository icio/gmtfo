gmtfo
=====

Get Me The Fuck Out: My hackathon entry for Duedil's internal 24-hour competition.

Disclaimer: Had to change tack about 12 hours in and didn't manage to do the text-parsing as I had hoped (lots of wasted time, sigh). Pathfinding was completed with 4 minutes to go on account of that and my first 4 attempts failing on account of exhaustion. It's still pretty buggy, doesn't allow you to specify the number of steps (you can do so by changing the `steps=1`) default of `compute_routes`, which I recommend and if there's no routes between two places then neither marker is added to the map, which is confusing: basically, there's not a lot of error handling and it errors out when there's no routes in some places. Loads more that I want to do with it: `/routes/` requests will parse out time references individually, the idea being that you would be able to say when you wanted to travel and it's highlight the list of days in calendar form in the #calendar element, but ah... was a great day!


Setup
-----

```bash
virtualenv env
. activate
pip install -r requirements.txt
python -m gmtfo.db
./httpd
```
