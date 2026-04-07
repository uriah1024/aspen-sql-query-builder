import json, urllib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from os.path import abspath
from flask import Flask

refugee_df = pd.read_csv(abspath('/Users/[USER]/Documents/Aspen/Pando_Ticket_Data/test.csv'))

print(refugee_df.head(5))

fig = go.Figure(data=[go.Sankey(
    node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label =  refugee_df['Node, Label'].dropna(axis=0, how='any'),
        color = refugee_df['Color']
    ),
    link = dict(
        source = refugee_df['Source'].dropna(axis=0, how='any'),
        target = refugee_df['Target'].dropna(axis=0, how='any'),
        value = refugee_df['Value'].dropna(axis=0, how='any'),
        color = refugee_df['Link Color'].dropna(axis=0, how='any')
))])

fig.update_layout(title_text="Basic Sankey Diagram - Aspen Technical Support - 4/1/2014 to 12/31/2019", font_size=10)
fig.show()