from os.path import abspath

with open('C:/python/live_files/uat_cps_node_urls.txt') as urls:
    for line in urls:
        url = line.rstrip('\n')
        # grab the deployment ID for Teams message, if needed.
        if url != '':
            deploymentId = url.split('//', 1)
            deploymentId = deploymentId[1].split('.')[0]
            port = url.split(':', 2)
            port = port[2].split('/')[0]
            cpsId = '{}:{}'.format(deploymentId, port)
            print(cpsId)
urls.close()