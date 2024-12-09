# ECON 895 - Project II

## Overview
`market_sim_api.py`: Sets up the Tkinter GUI for the user to interact with.
`tournament.py`: Runs the tournament for a number of rounds determined by the user.
`market_simulator_v2.py`: Runs an independent simulation for selected traders by user.
`spot_market_environment.py`: Contains functions to develop market participants, the demand curve, the supply curve, and calculates competitive equilibrium.
`double_auction.py`: Develops and runs an order book of bidding, selling, and contracts between market participants.
`buyer.py`: Contains buyer bidding strategies.
`seller.py`: Contains seller selling strategies.

## Tkinter GUI
The Tkinter GUI is set up to allow a user to first select whether they would like to load a TOML configuration file or use a dropdown menu to select the strategies for each buyer and seller the user adds.

Using the dropdown menu, the user can select from four premade bidding/selling strategies found in either the buyer or seller modules. The user then saves the TOML file and is immediately prompted to load it before continuing.

After selecting a TOML configuration file or using the dropdown menu, the user can then run a single simulation or a tournament with multiple rounds of simulations. If the user wishes to run a tournament, they must first type out how many rounds they would like to conduct.

The tournament results provide a neat printout and plots of the simulation results.

There is a quit button for the user to exit the program.

## Bidding/Selling Strategies
`Zero Intelligence`: Included in base buyer and seller modules. The strategy is to make a random bid between the standing bid (standing ask) and the current reservation value (unit cost) of the buyer (seller).

`Kaplan`: Modeled after the 'Kaplan' bidding strategy in Rust et al. (1994, p. 73). The strategy is to wait and let others exchange, but when the spread gets sufficiently close, jump in to "steal the deal."

`Ringuette`: Modeled after the 'Ringuette' bidding strategy in Rust et al. (1994, p. 74). Like the 'Kaplan' strategy, wait and let others exchange, but when the spread gets sufficiently close, jump in to "steal the deal."

`Persistent Shout`: Modeled after the 'Persistent Shout' bidding strategy in Priest & Tol (2003).

`Skeleton`: Modeled after the 'Skeleton' strategy bidding strategy in Rust et al. (1994, p. 75). The base strategy provided by the authors was supplied to all entrants of a double auction tournament.

## Instructions to Run GUI

Simply run: `python market_sim.api.py`

You can also access the `ECON895_ProjectII_Notebook.ipynb` to see my answers to the project's specific questions and run the GUI from there.