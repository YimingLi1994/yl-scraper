profile = {
    'test_index': {
        'status_server': ['127.0.0.1', 10058],
        'distributor_server': ['127.0.0.1', 10059],
        'receiver_server': ['127.0.0.1', 10060],
        'storage_name_filter': 'scraper_general',#'test_index',
        'distributor_key': 'aewrkjwearofikjwsewthewldamnmrykqwoaslxmnzvp40ekt85kj',
        'receiver_key': 'agwreaeg$KLZ!@}Kwthnwstrgarfga4',
        'statuskey': '23rafaerfargareg',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.5,  # number of max scraping speed(n/s) per worker
    },
    'HA_scraping': {
        'status_server': ['10.142.0.4', 20055],
        'distributor_server': ['10.142.0.4', 20060],
        'receiver_server': ['10.142.0.4', 20070],
        'vm_name_filter': 'ha-scraping',
        'storage_name_filter': 'HA_scraping',
        'start_up_script': 'ha_scraping.sh',
        'distributor_key': 'afeifjaorigjoaijgr',
        'receiver_key': 'awefawepfjpoaijdofgv',
        'statuskey': 'awgerqwergaefrdgadfhbgabgaewrgbawergbv',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.2,  # number of max scraping speed(n/s) per worker
        'conversion_rate': 600,
        'vm_lmt': 200,
        'vm_lifecycle': 25
    },
    'amazon_scraping': {
        'status_server': ['10.142.0.4', 10055],
        'distributor_server': ['10.142.0.4', 10060],
        'receiver_server': ['10.142.0.4', 10070],
        'vm_name_filter': 'amazon-scraping',
        'storage_name_filter': 'amazon_scraping',
        'start_up_script': 'amazon_scraping.sh',
        'distributor_key': 'aefaegarhaerhaewaewfadsfturejye',
        'receiver_key': 'faerfargthykwgserte5jdsthserw34t',
        'statuskey': 'sthsrthjasethsergasergdjkty',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.15,  # number of max scraping speed(n/s) per worker
        'conversion_rate': 400,
        'vm_lmt': 600,
        'vm_lifecycle': 25
    },
    'general_scraping': {
        'status_server': ['10.142.0.4', 10013],
        'distributor_server': ['10.142.0.4', 10014],
        'receiver_server': ['10.142.0.4', 10015],
        'vm_name_filter': 'scraper-general',
        'storage_name_filter': 'scraper_general',
        'start_up_script': 'worker_general.sh',
        'distributor_key': 'aefjoargnoanrgoansd',
        'receiver_key': 'aporkgpaokrpgoadfgv',
        'statuskey': 'aoperkgopakerpogapvaporgk',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.2,  # number of max scraping speed(n/s) per worker
        'conversion_rate': 400,
        'vm_lmt': 300,
        'vm_lifecycle': 25
    },
    'slow_scraping': {
        'status_server': ['10.142.0.4', 9013],
        'distributor_server': ['10.142.0.4', 9014],
        'receiver_server': ['10.142.0.4', 9015],
        'vm_name_filter': 'slow-scraping',
        'storage_name_filter': 'slow_scraping',
        'start_up_script': 'slow_scraping.sh',
        'distributor_key': 'aefargastrharg',
        'receiver_key': 'ahtrerfghaefrgaergaer',
        'statuskey': 'aergaergaethaetheatrh',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.15,  # number of max scraping speed(n/s) per worker
        'conversion_rate': 10,
        'vm_lmt': 25,
        'vm_lifecycle': 25
    },
    'amz_flash': {
        'status_server': ['10.142.0.4', 9016],
        'distributor_server': ['10.142.0.4', 9017],
        'receiver_server': ['10.142.0.4', 9018],
        'vm_name_filter': 'amz-flash',
        'storage_name_filter': 'amz_flash',
        'start_up_script': 'amz_flash.sh',
        'distributor_key': 'safaefawefawdfafgsdfghad',
        'receiver_key': 'arehgaergaergawrefgaeefrgag',
        'statuskey': 'aergaergafdehgsrthsrthsryjfdjkg',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.15,  # number of max scraping speed(n/s) per worker
        'conversion_rate': 500,
        'vm_lmt': 150,
        'vm_lifecycle': 25
    },
    'site_map_walk': {
        'status_server': ['10.142.0.4', 8016],
        'distributor_server': ['10.142.0.4', 8017],
        'receiver_server': ['10.142.0.4', 8018],
        'vm_name_filter': 'site-map',
        'storage_name_filter': 'site_map',
        'start_up_script': 'site_map.sh',
        'distributor_key': 'aefiajeoigjioaheg',
        'receiver_key': 'arargw6je5hjewrtghse5grtse',
        'statuskey': 'arhaegrtarhrjtuekmtydhrt',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.15,  # number of max scraping speed(n/s) per worker
        'conversion_rate': 500,
        'vm_lmt': 150,
        'vm_lifecycle': 25
    },
    'test_server': {
        'status_server': ['10.142.0.4', 18016],
        'distributor_server': ['10.142.0.4', 18017],
        'receiver_server': ['10.142.0.4', 18018],
        'vm_name_filter': 'test-server',
        'storage_name_filter': 'test_server',
        'start_up_script': 'test_server.sh',
        'distributor_key': 'wiejfoqoeimoimom',
        'receiver_key': 'iajoerifjaoiemomag',
        'statuskey': 'iosjorogimsorimokamfdkvalkdmfo',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.15,  # number of max scraping speed(n/s) per worker
        'conversion_rate': 500,
        'vm_lmt': 20,
        'vm_lifecycle': 25
    },
    'ad_hoc': {
        'status_server': ['10.142.0.4', 11016],
        'distributor_server': ['10.142.0.4', 11017],
        'receiver_server': ['10.142.0.4', 11018],
        'vm_name_filter': 'ad-hoc',
        'storage_name_filter': 'ad_hoc',
        'start_up_script': 'ad_hoc.sh',
        'distributor_key': 'adhocwiejfoqoeimoimom',
        'receiver_key': 'adhociajoerifjaoiemomag',
        'statuskey': 'adhociosjorogimsorimokamfdkvalkdmfo',
        'recycle_timeout': 200,
        'retry_lmt': 2,
        'distribution_lmt': 4,
        'speed_per_worker': 0.15,  # number of max scraping speed(n/s) per worker
        'conversion_rate': 500,
        'vm_lmt': 40,
        'vm_lifecycle': 25
    }

}
