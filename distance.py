import streamlit as st
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import taxicab as tc

def show():
    st.title("Distance Visualization between Student and Company")

    # User input for coordinates
    lat, lon = {}, {}
    location_labels = ["student", "company"]
    
    for label in location_labels:
        st.write(label)
        location = st.columns(2)
        precision = "{:.10f}".format
        lat[label] = location[0].number_input(f"{label} Latitude", key=f"lat_{label}")
        lon[label] = location[1].number_input(f"{label} Longitude", key=f"lon_{label}")
        

    # Check if both locations are provided
    if all(lat.values()) and all(lon.values()):
        xmin, xmax = min(lon.values()),max(lon.values())
        ymin, ymax = min(lat.values()), max(lat.values())

        xmin, xmax = lon["Student"], lon["Company"] + .005
        ymin, ymax = lat["Student"], lat["Company"] + .005

        # Create graph from bounding box
        G = ox.graph_from_bbox(ymax, ymin, xmin, xmax, network_type="drive", simplify=True)

        # Origin and destination points
        orig = (lat["student"], lon["student"])
        dest = (lat["company"], lon["company"])

        # Calculate shortest path
        route = tc.distance.shortest_path(G, orig, dest)
        st.write(f"Distance from student house to company: {round(route[0], 2)}m")

        # Plot and display the route
        fig, ax = tc.plot.plot_graph_route(G, route, figsize=(20, 20), show=False, close=False)

        ax.scatter(orig[1], orig[0], color="lime", marker="X", s=50, label="Student")
        ax.scatter(dest[1], dest[0], color="red", marker="X", s=50, label="Company")

        # Adjust the plot view
        pad = .01
        ax.set_ylim([min([orig[0], dest[0]]) - pad, max([orig[0], dest[0]]) + pad])
        ax.set_xlim([min([orig[1], dest[1]]) - pad, max([orig[1], dest[1]]) + pad])

        plt.legend()
        st.pyplot(fig)

show()
