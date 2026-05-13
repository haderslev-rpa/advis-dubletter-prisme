
def behandel_page(item):
    print("Nu kører koden i behandl.py")

    data = item.data

    from q_prisme365_api.advis_update import update_advis
    from q_haderslev_vbo.automation_server.ats_update_item_data import update_item_data

    success =update_advis(data["box"]["RecIdLoc"], handled=True)

    update_item_data(
        data,
        state_updates={
            "State": "Advis behandlet i Prisme",
        },
    )
    item.update(data) #update data.
                