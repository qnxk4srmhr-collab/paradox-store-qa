def open_url(page, url):
    """Go to a store page, and fail straight away if the site refuses to serve it.

    Without this check, an error page (for example 429 Too Many Requests, when the
    store rate-limits us) only shows up later as a confusing 30-second timeout
    while waiting for products that never appear.
    """
    response = page.goto(url)
    # goto returns None when only the #fragment changes; there's nothing to check then.
    if response is not None:
        assert response.ok, (
            f"{url} returned HTTP {response.status}. "
            "429 means the store is rate-limiting this machine: wait a while before running again."
        )
