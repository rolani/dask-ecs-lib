# utility functions

def parse_url(s):
    """
    Converts returned cluster details to url to visit for dask dashboard
    """

    s_ = s.split(",")
    s1_ = s_[1].split("/")
    s2_ = s1_[2].split(":")
    url_ = "http://" + s2_[0] + ":8787"
    return url_

def estimate_cost(estimate_per_hr, elapsed_time):
    """
    Returns cost estimate of using the cluster
    """

    return estimate_per_hr * elapsed_time / 3600