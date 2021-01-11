# Setup venv

Install venv (Linux):
`apt install python3-venv`

Create venv folder:
`python3 -m venv venv`

Activate venv:
`source venv/bin activate`

# Installation

Install packages:
`pip install -r requirements.txt`

# Update Package List

Add new packages:
`pip install <package-name>`

Then record environment's current package list:
`pip freeze > requirements.txt`
