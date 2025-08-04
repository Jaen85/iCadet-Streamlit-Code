# import osmnx as ox
# import networkx as nx
# import pandas as pd
# import numpy as np
# from haversine import haversine, Unit
# from tqdm.notebook import tqdm
# import taxicab as tc
# import os
# import pandana as pdna
# import streamlit as st
# import math
# import matplotlib.pyplot as plt

# import warnings
# warnings.filterwarnings("ignore")

# def calculate_driving_distance(student_location,company_location):
#     student_lat, student_lon = student_location
#     company_lat, company_lon = company_location
    
#     # Margin of error in degrees for 2 km
#     lat_margin = 2 / 111 
#     lon_margin_student = 2 / (111 * math.cos(math.radians(student_lat)))
#     lon_margin_company = 2 / (111 * math.cos(math.radians(company_lat)))

#     # Apply the margin of error
#     xmin, xmax = min(student_lon, company_lon) - lon_margin_student, max(student_lon, company_lon) + lon_margin_company
#     ymin, ymax = min(student_lat, company_lat) - lat_margin, max(student_lat, company_lat) + lat_margin
    
#     G = ox.graph_from_bbox(north=ymax, south=ymin, east=xmax, west=xmin, network_type='drive', simplify=True)
    
#     student_node = ox.distance.nearest_nodes(G, X=student_lon, Y=student_lat)
#     company_node = ox.distance.nearest_nodes(G, X=company_lon, Y=company_lat)
    
#     try:
#         route = nx.shortest_path_length(G,student_node, company_node, weight='length')
#         return route / 1000
#     except nx.NetworkXNoPath:
#          return tc.distance.shortest_path(G, student_location, company_location)[0]
    
# def calculate_and_plot_route(student_location, company_location):
#     driving_distance = calculate_driving_distance(student_location, company_location)

#    # Creating the graph from bounding box
#     xmin, xmax = min(student_location[1], company_location[1]), max(student_location[1], company_location[1])
#     ymin, ymax = min(student_location[0], company_location[0]), max(student_location[0], company_location[0])
#     G = ox.graph_from_bbox(north=ymax, south=ymin, east=xmax, west=xmin, network_type='drive', simplify=True)


#     # Plotting the route
#     route = tc.distance.shortest_path(G, student_location, company_location)
#     fig, ax = tc.plot.plot_graph_route(G, route, figsize=(20, 20), show=False, close=False)

#     ax.scatter(student_location[1], student_location[0], color="lime", marker="X", s=50, label="Student")
#     ax.scatter(company_location[1], company_location[0], color="red", marker="X", s=50, label="Company")

#     pad = .01
#     ax.set_ylim([min([student_location[0], company_location[0]]) - pad, max([student_location[0], company_location[0]]) + pad])
#     ax.set_xlim([min([student_location[1], company_location[1]]) - pad, max([student_location[1], company_location[1]]) + pad])

#     plt.legend()
#     return fig, driving_distance

# def assign_student_to_company(student_lat, student_lon, student_major_code, company_lat, company_lon, company_major_code):
#     student_location = (student_lat, student_lon)
#     company_location = (company_lat, company_lon)

#     if student_major_code == company_major_code:
#         fig, driving_distance = calculate_and_plot_route(student_location, company_location)
#         assignment = {
#             'Student Major Code': student_major_code,
#             'Company Major Code': company_major_code,
#             'Driving Distance (km)': driving_distance
#         }
#         return assignment, fig
#     else:
#         return "Major codes do not match.", None
    
# def main():
#     st.title("iCadet Assignment Interface")

#     # User inputs for student
#     st.header("Student Details")
#     student_lat = st.number_input("Student Latitude", format="%.6f")
#     student_lon = st.number_input("Student Longitude", format="%.6f")
#     student_major_code = st.text_input("Student Major Code")

#     # User inputs for company
#     st.header("Company Details")
#     company_lat = st.number_input("Company Latitude", format="%.6f")
#     company_lon = st.number_input("Company Longitude", format="%.6f")
#     company_major_code = st.text_input("Company Major Code")

#     submit_button = st.button("Assign Student to Company")

#     if submit_button:
#         # Ensure all required arguments are passed to the function
#         assignment_result, route_fig = assign_student_to_company(
#             student_lat, student_lon, student_major_code, 
#             company_lat, company_lon, company_major_code
#         )

#         # Process the result and display
#         if route_fig is not None:
#             st.write(assignment_result)
#             st.pyplot(route_fig)
#         else:
#             st.write("Assignment failed:", assignment_result)
                                                                 
# if __name__ == "__main__":
#     main()

import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from haversine import haversine, Unit
from tqdm.notebook import tqdm
import taxicab as tc
import os
import pandana as pdna
import streamlit as st
import math
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")


def calculate_driving_distance(student_location, company_location):
    student_lat, student_lon = student_location
    company_lat, company_lon = company_location

    # Margin of error in degrees for 2 km
    lat_margin = 2 / 111
    lon_margin_student = 2 / (111 * math.cos(math.radians(student_lat)))
    lon_margin_company = 2 / (111 * math.cos(math.radians(company_lat)))

    # Apply the margin of error
    north = max(student_lat, company_lat) + lat_margin
    south = min(student_lat, company_lat) - lat_margin
    east = max(student_lon, company_lon) + max(lon_margin_student, lon_margin_company)
    west = min(student_lon, company_lon) - max(lon_margin_student, lon_margin_company)

    # Use bbox parameter instead of individual north, south, east, west parameters
    try:
        # For newer versions of OSMnx (1.0+)
        G = ox.graph_from_bbox(bbox=(north, south, east, west), network_type='drive', simplify=True)
    except TypeError:
        try:
            # Alternative approach for different OSMnx versions
            G = ox.graph_from_bbox(north, south, east, west, network_type='drive', simplify=True)
        except TypeError:
            # Fallback for older versions
            G = ox.graph_from_bbox(north=north, south=south, east=east, west=west, network_type='drive', simplify=True)

    # Get nearest nodes
    student_node = ox.distance.nearest_nodes(G, X=student_lon, Y=student_lat)
    company_node = ox.distance.nearest_nodes(G, X=company_lon, Y=company_lat)

    try:
        route = nx.shortest_path_length(G, student_node, company_node, weight='length')
        return route / 1000  # meters to km
    except nx.NetworkXNoPath:
        return tc.distance.shortest_path(G, student_location, company_location)[0]


def calculate_and_plot_route(student_location, company_location):
    driving_distance = calculate_driving_distance(student_location, company_location)

    # Set up same bounding box margins
    lat_margin = 2 / 111
    lon_margin_student = 2 / (111 * math.cos(math.radians(student_location[0])))
    lon_margin_company = 2 / (111 * math.cos(math.radians(company_location[0])))

    north = max(student_location[0], company_location[0]) + lat_margin
    south = min(student_location[0], company_location[0]) - lat_margin
    east = max(student_location[1], company_location[1]) + max(lon_margin_student, lon_margin_company)
    west = min(student_location[1], company_location[1]) - max(lon_margin_student, lon_margin_company)

    # Use the same approach as in calculate_driving_distance
    try:
        # For newer versions of OSMnx (1.0+)
        G = ox.graph_from_bbox(bbox=(north, south, east, west), network_type='drive', simplify=True)
    except TypeError:
        try:
            # Alternative approach for different OSMnx versions
            G = ox.graph_from_bbox(north, south, east, west, network_type='drive', simplify=True)
        except TypeError:
            # Fallback for older versions
            G = ox.graph_from_bbox(north=north, south=south, east=east, west=west, network_type='drive', simplify=True)

    # Plotting the route
    route = tc.distance.shortest_path(G, student_location, company_location)
    fig, ax = tc.plot.plot_graph_route(G, route, figsize=(20, 20), show=False, close=False)

    # Plot student and company points
    ax.scatter(student_location[1], student_location[0], color="lime", marker="X", s=100, label="Student")
    ax.scatter(company_location[1], company_location[0], color="red", marker="X", s=100, label="Company")

    # Adjust axis limits
    pad = .01
    ax.set_ylim([min([student_location[0], company_location[0]]) - pad, max([student_location[0], company_location[0]]) + pad])
    ax.set_xlim([min([student_location[1], company_location[1]]) - pad, max([student_location[1], company_location[1]]) + pad])

    plt.legend()
    return fig, driving_distance


def assign_student_to_company(student_lat, student_lon, student_major_code, company_lat, company_lon, company_major_code):
    student_location = (student_lat, student_lon)
    company_location = (company_lat, company_lon)

    if student_major_code == company_major_code:
        fig, driving_distance = calculate_and_plot_route(student_location, company_location)
        assignment = {
            'Student Major Code': student_major_code,
            'Company Major Code': company_major_code,
            'Driving Distance (km)': round(driving_distance, 2)
        }
        return assignment, fig
    else:
        return "Major codes do not match.", None


def main():
    st.title("iCadet Assignment Interface")

    # User inputs for student
    st.header("Student Details")
    student_lat = st.number_input("Student Latitude", format="%.6f")
    student_lon = st.number_input("Student Longitude", format="%.6f")
    student_major_code = st.text_input("Student Major Code")

    # User inputs for company
    st.header("Company Details")
    company_lat = st.number_input("Company Latitude", format="%.6f")
    company_lon = st.number_input("Company Longitude", format="%.6f")
    company_major_code = st.text_input("Company Major Code")

    submit_button = st.button("Assign Student to Company")

    if submit_button:
        # Validate inputs
        if not all([student_lat, student_lon, student_major_code, company_lat, company_lon, company_major_code]):
            st.error("Please fill in all fields before submitting.")
            return
            
        assignment_result, route_fig = assign_student_to_company(
            student_lat, student_lon, student_major_code,
            company_lat, company_lon, company_major_code
        )

        if route_fig is not None:
            st.success("Assignment successful!")
            st.write(assignment_result)
            st.pyplot(route_fig)
        else:
            st.error(f"Assignment failed: {assignment_result}")


if __name__ == "__main__":
    main()