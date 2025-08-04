import streamlit as st
import pandas as pd
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import taxicab as tc
import math
import warnings
from joblib import Parallel, delayed

warnings.filterwarnings("ignore", category=FutureWarning, module='osmnx')

faculty_domains = {
    'FCA': ['Creative producing', 'Cinematography', 'Cinematics Arts'],
    'FAC': ['Applied Communication', 'Strategic Communication'],  
    'FCI': ['Data science', 'Software engineering', 'Game development', 'Cybersecurity', 'Information System'],
    'FIST': ['Artificial Intelligence', 'Data Communication and Networking', 'Business Intelligence and Analytics','Security Technology'], 
    'FCM': ['Interface Design', 'Virtual Reality', 'Media Arts','Animation','Advertising Design','Visual Effects','Animation & Visual Effects'], 
    'FOE': ['Electronics', 'Electrical', 'Electronic Majoring in Computer','Electronics Majoring in Communications','Intellgent Robotics'], 
    'FOM': ['Accounting', 'Finance', 'Marketing','Business Management','Digital Enterprise Management','Analytical Economics','Financial Engineering'],  
    'FOB': ['Accounting', 'Human Resource Management', 'Banking and Finance','Marketing Management','International Management','Digital Business Management','Knowledge Management'],  
    'FOL': ['Law'],  
    'FET': ['Electronic Engineering', 'Electronics Majoring in Robotics & Automation', 'Mechanical Engineering']  
}

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371
    return c * r

def create_graph_from_bbox(north, south, east, west):
    try:
        return ox.graph_from_bbox((north, south, east, west), network_type='drive', simplify=True)
    except Exception as e:
        st.error(f"Graph creation failed: {e}")
        return None

def calculate_driving_distance(student_location, company_location, G):
    student_lat, student_lon = student_location
    company_lat, company_lon = company_location
    try:
        student_node = ox.distance.nearest_nodes(G, X=student_lon, Y=student_lat)
        company_node = ox.distance.nearest_nodes(G, X=company_lon, Y=company_lat)
        route_length = nx.shortest_path_length(G, student_node, company_node, weight='length')
        return route_length / 1000
    except Exception:
        try:
            return tc.distance.distance(student_location, company_location)
        except:
            return haversine(student_lat, student_lon, company_lat, company_lon)

def calculate_and_plot_route(student_location, company_location, G):
    student_lat, student_lon = student_location
    company_lat, company_lon = company_location
    fig, ax = None, None
    route_plotted = False
    driving_distance = None

    try:
        student_node = ox.distance.nearest_nodes(G, X=student_lon, Y=student_lat)
        company_node = ox.distance.nearest_nodes(G, X=company_lon, Y=company_lat)
        st.write(f"Student node: {student_node}, Company node: {company_node}")
        route = nx.shortest_path(G, student_node, company_node, weight='length')
        driving_distance = nx.shortest_path_length(G, student_node, company_node, weight='length') / 1000
        fig, ax = ox.plot_graph_route(G, route, figsize=(15, 15), route_linewidth=6, route_color='orange', show=False, close=False)
        route_plotted = True
    except Exception as e:
        st.warning(f"Routing failed: {e}")
        try:
            driving_distance = tc.distance.distance(student_location, company_location)
        except:
            driving_distance = haversine(student_lat, student_lon, company_lat, company_lon)

    if not route_plotted:
        try:
            fig, ax = ox.plot_graph(G, figsize=(15, 15), show=False, close=False, node_color='white', node_size=30, edge_color='gray', edge_linewidth=1)
        except:
            return None, driving_distance

    ax.scatter(student_lon, student_lat, color="lime", marker="X", s=50, label="Student", zorder=10, edgecolors='black', linewidth=1)
    ax.scatter(company_lon, company_lat, color="red", marker="X", s=50, label="Company", zorder=10, edgecolors='black', linewidth=1)
    pad_lat = max(0.001, abs(student_lat - company_lat) * 0.1)
    pad_lon = max(0.001, abs(student_lon - company_lon) * 0.1)
    ax.set_ylim([min(student_lat, company_lat) - pad_lat, max(student_lat, company_lat) + pad_lat])
    ax.set_xlim([min(student_lon, company_lon) - pad_lon, max(student_lon, company_lon) + pad_lon])
    plt.legend(loc='upper right', fontsize=12)
    title = f"Route: Distance = {driving_distance:.2f} km" if driving_distance is not None else "Route: Distance Unavailable"
    plt.title(title)
    plt.tight_layout()
    return fig, driving_distance

def assign_student_to_company(student_id, student_lat, student_lon, student_domain, student_faculty, companies_df):
    student_location = (student_lat, student_lon)
    companies_df = companies_df.copy()
    companies_df['Major'] = companies_df['Major'].str.lower()
    matching = companies_df[(companies_df['Major'] == student_domain.lower()) & (companies_df['Faculty'] == student_faculty)]
    matching = matching.dropna(subset=['Latitude', 'Longitude'])
    if matching.empty:
        return "No matching companies found.", None
    matching['Haversine'] = matching.apply(lambda r: haversine(student_lat, student_lon, r['Latitude'], r['Longitude']), axis=1)
    nearby = matching[matching['Haversine'] <= 50]
    if nearby.empty:
        return "No companies within threshold.", None
    all_lats = [student_lat] + nearby['Latitude'].tolist()
    all_lons = [student_lon] + nearby['Longitude'].tolist()
    G = create_graph_from_bbox(max(all_lats)+0.02, min(all_lats)-0.02, max(all_lons)+0.02, min(all_lons)-0.02)
    if G is None:
        return "Graph creation failed.", None
    def compute_dist(r):
        try:
            return calculate_driving_distance(student_location, (r['Latitude'], r['Longitude']), G)
        except:
            return None
    nearby['Driving'] = [compute_dist(r) for i, r in nearby.iterrows()]
    nearby = nearby.dropna(subset=['Driving'])
    if nearby.empty:
        return "No valid distances.", None
    best = nearby.loc[nearby['Driving'].idxmin()]
    fig, driving_distance = calculate_and_plot_route(student_location, (best['Latitude'], best['Longitude']), G)
    result = {
        'Student ID': student_id,
        'Student Faculty': student_faculty,
        'Company Domain': best['Major'],
        'Company Name': best['Company'],
        'Driving Distance (km)': round(driving_distance, 2) if driving_distance is not None else 'N/A'
    }
    return result, fig

def student_company_assignment():
    col1, col2, col3 = st.columns([1,1,50])
    with col2:
        try:
            st.image("MMU logo.png", width=200)
        except:
            st.markdown("### Multimedia University")
    st.title("Student-Company Assignment")
    student_id = st.text_input("Student ID")
    student_lat = st.number_input("Latitude", format="%.6f")
    student_lon = st.number_input("Longitude", format="%.6f")
    faculty = st.selectbox("Faculty", list(faculty_domains.keys()))
    domain = st.selectbox("Domain", faculty_domains[faculty])
    if st.button("Submit"):
        df = pd.read_csv('/Users/angeline/Downloads/FYP Code/Streamlit/itp_companies.csv')
        assignment, fig = assign_student_to_company(student_id, student_lat, student_lon, domain, faculty, df)
        if fig:
            st.dataframe(pd.DataFrame([assignment]))
            st.pyplot(fig)
        else:
            st.warning(assignment)

if __name__ == '__main__':
    student_company_assignment()
