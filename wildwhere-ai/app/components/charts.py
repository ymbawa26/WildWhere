import plotly.express as px


COLOR_SEQUENCE = ["#7FB069", "#D9A441", "#D66A50", "#6CA6C1", "#C7D6C1", "#B08BBB"]


def bar_chart(df, x, y, title, color=None):
    fig = px.bar(df, x=x, y=y, color=color, title=title, color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0F1714", plot_bgcolor="#17231F", title_x=0.02)
    return fig


def line_chart(df, x, y, title, color=None):
    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title, color_discrete_sequence=COLOR_SEQUENCE)
    fig.update_layout(template="plotly_dark", paper_bgcolor="#0F1714", plot_bgcolor="#17231F", title_x=0.02)
    return fig
