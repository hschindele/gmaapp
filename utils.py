import dash_html_components as html
import dash_core_components as dcc


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
