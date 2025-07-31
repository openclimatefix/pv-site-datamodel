"""
Example usage of the new management and details functions.

This file demonstrates how to use the newly added functions for managing
site groups and getting detailed information about users, sites, and site groups.
"""

from pvsite_datamodel.connection import DatabaseConnection
from pvsite_datamodel.read import (
    get_user_details,
    get_site_details,
    get_site_group_details,
    validate_email,
)
from pvsite_datamodel.management import (
    add_all_sites_to_site_group,
    change_user_site_group,
    get_all_client_site_ids,
    get_all_site_uuids,
    select_site_by_client_id,
    select_site_by_uuid,
    update_site_group,
)


def example_usage():
    """Example of how to use the new functions."""
    
    # Create database connection
    # Replace with your actual database URL
    db = DatabaseConnection(url="postgresql://user:password@localhost/database")
    
    with db.get_session() as session:
        
        # Example 1: Get all site UUIDs
        print("Getting all site UUIDs...")
        site_uuids = get_all_site_uuids(session)
        print(f"Found {len(site_uuids)} sites")
        
        # Example 2: Get all client site IDs
        print("\nGetting all client site IDs...")
        client_ids = get_all_client_site_ids(session)
        print(f"Found {len(client_ids)} client IDs")
        
        # Example 3: Validate email addresses
        print("\nValidating email addresses...")
        emails = ["valid@example.com", "invalid-email", "another@valid.org"]
        for email in emails:
            is_valid = validate_email(email)
            print(f"{email}: {'Valid' if is_valid else 'Invalid'}")
        
        # Example 4: Get user details (if user exists)
        user_email = "user@example.com"  # Replace with actual email
        try:
            user_sites, user_site_group, user_site_count = get_user_details(session, user_email)
            print(f"\nUser {user_email}:")
            print(f"  Site group: {user_site_group}")
            print(f"  Number of sites: {user_site_count}")
            print(f"  Sites: {user_sites[:3]}...")  # Show first 3 sites
        except Exception as e:
            print(f"\nCould not get details for user {user_email}: {e}")
        
        # Example 5: Get site details (if site exists)
        if site_uuids:
            site_uuid = site_uuids[0]  # Use first site
            try:
                site_details = get_site_details(session, site_uuid)
                print(f"\nSite details for {site_uuid}:")
                print(f"  Client ID: {site_details['client_site_id']}")
                print(f"  Name: {site_details['client_site_name']}")
                print(f"  Country: {site_details['country']}")
                print(f"  Asset type: {site_details['asset_type']}")
                print(f"  Capacity: {site_details['capacity']}")
            except Exception as e:
                print(f"\nCould not get details for site {site_uuid}: {e}")
        
        # Example 6: Get site group details
        site_group_name = "ocf"  # Replace with actual site group name
        try:
            group_sites, group_users = get_site_group_details(session, site_group_name)
            print(f"\nSite group '{site_group_name}':")
            print(f"  Number of sites: {len(group_sites)}")
            print(f"  Number of users: {len(group_users)}")
            print(f"  Sites: {group_sites[:3]}...")  # Show first 3 sites
            print(f"  Users: {group_users[:3]}...")  # Show first 3 users
        except Exception as e:
            print(f"\nCould not get details for site group {site_group_name}: {e}")
        
        # Example 7: Select site by UUID (validation)
        if site_uuids:
            try:
                validated_uuid = select_site_by_uuid(session, site_uuids[0])
                print(f"\nValidated site UUID: {validated_uuid}")
            except ValueError as e:
                print(f"\nSite validation failed: {e}")
        
        # Example 8: Select site by client ID (validation)
        if client_ids:
            try:
                site_uuid_from_client_id = select_site_by_client_id(session, client_ids[0])
                print(f"\nSite UUID from client ID {client_ids[0]}: {site_uuid_from_client_id}")
            except ValueError as e:
                print(f"\nClient ID validation failed: {e}")


if __name__ == "__main__":
    # This is just an example - you would need to set up your database connection
    print("This is an example usage file.")
    print("To use these functions, set up your database connection and call the functions as shown.")
    print("See the example_usage() function for detailed examples.")
