import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

SIDEBAR_STYLE = {
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "10rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H5("Page Select"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/home", active="exact"),
                dbc.NavLink("Records and Rankings", href="/records-and-rankings", active="exact"),
                dbc.NavLink("Player Search", href="/player-search", active="exact"),
                dbc.NavLink("Archive", href="/archive", active="exact")
            ],
            vertical=True,
            pills=True
        ),
        html.Hr(),
        html.H5("Mountain Pages"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Hirschalm đŚđš", href="/hirschalm", active="exact"),
                dbc.NavLink("Waldtal đŠđŞ", href="/waldtal", active="exact"),
                dbc.NavLink("Elnakka đŤđŽ", href="/elnakka", active="exact"),
                dbc.NavLink("Dalarna đ¸đŞ", href="/dalarna", active="exact"),
                dbc.NavLink("Rotkamm đ¨đ­", href="rotkamm", active="exact"),
                dbc.NavLink("Saint Luvette đŤđˇ", href="/saintluvette", active="exact"),
                dbc.NavLink("Passo Grolla đŽđš", href="/passogrolla", active="exact"),
                dbc.NavLink("Ben Ailig đ´ó §ó ˘ó łó Łó ´ó ż", href="/benailig", active="exact"),
                dbc.NavLink("Mount Fairview đ¨đŚ", href="/mountfairview", active="exact"),
                dbc.NavLink("Pinecone Peaks đşđ¸", href="/pineconepeaks", active="exact"),
                dbc.NavLink("Agpat Island đŹđą", href="/agpatisland", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

def Header(app):
    return html.Div([get_header(app)])


def get_header(app):
    header = html.Div(
        [
            html.Img(src=app.get_asset_url('gmalogo.png'),
                     className='logo',
                     style={'height':'280px', 'width':'auto'})
        ],
        className="row",
    )
    return header


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table
