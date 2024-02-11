# GPU
gcloud compute instances create gpu-belgium-1 \
    --project=law-2006463162 \
    --zone=europe-west1-d \
    --machine-type=custom-4-8192 \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=TERMINATE \
    --provisioning-model=STANDARD \
    --service-account=232168920061-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --accelerator=count=1,type=nvidia-tesla-t4 \
    --create-disk=auto-delete=yes,boot=yes,device-name=gpu-belgium-1-gpu,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20240126,mode=rw,size=80,type=projects/law-2006463162/zones/europe-west1-d/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any


# Controller
gcloud compute instances create controller-belgium-1 \
    --project=law-2006463162 \
    --zone=europe-west1-d \
    --machine-type=e2-custom-4-8192 \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --provisioning-model=STANDARD \
    --service-account=232168920061-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --create-disk=auto-delete=yes,boot=yes,device-name=gpu-belgium-1-controller,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20240126,mode=rw,size=80,type=projects/law-2006463162/zones/europe-west1-d/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any

