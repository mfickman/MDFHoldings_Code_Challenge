# MDFHoldings_Code_Challenge
Story:
As a developer I want to write a Web App that simulates one of our internal processes and displays it
over to a web interface.

Assignment/Overview:
Create a web app using Flask that emulates a basic telephone switchboard, this app will consist of two
parts.

The first part allows a user to summit “calls” via a POST request. The request will contain 3 fields, one is
the calling number ani, the second field is the callto number, the last field being what action to take,
either answer or hangup. The developer will need to validate each field and make sure numbers are
valid phone numbers, responding with a 400 or 200 depending on the request. All valid answer requests
will “place” the call on the system. All valid hangup requests will remove the call from the system.

The second part of the web app is to display the calls currently present on the system. Displaying who is
calling, where they are calling to, and how long it’s been on the system. This status page will show all
calls and a count up timer of how long each call has been online.

Acceptance Criteria:
- Write an example web application from scratch using Flask that accepts calls requests and display calls
present.
- Validate numbers are valid phone numbers
- Document all features and how to’s for the web app
- Use git. Submit your repo (zip, dropbox link, etc) back to the email thread.
- Use Python 3

Bonus Points:
- A history page showing all calls
- A request log file
- SQL (sqlite3) persistence of calls placed

Deadline:
One week from the delivery of these instructions

Note:
We are not asking you to create a service for us, this is entirely an assessment of your knowledge of
Python and to a lower extent, HTML, CSS and JavaScript.
