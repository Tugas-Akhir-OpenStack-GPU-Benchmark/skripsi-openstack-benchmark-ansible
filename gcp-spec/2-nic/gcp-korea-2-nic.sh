# Tested
INSTANCE_ID=$RANDOM

# GPU
gcloud compute instances create korea-gpu-$INSTANCE_ID-2 \
    --project=law-2006463162 \
    --zone=asia-northeast3-c \
    --machine-type=custom-4-8192 \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --network-interface=aliases=/26,network-tier=STANDARD,stack-type=IPV4_ONLY,subnet=subnet-korea-1 \
    --maintenance-policy=TERMINATE \
    --provisioning-model=STANDARD \
    --service-account=232168920061-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --accelerator=count=1,type=nvidia-tesla-t4 \
    --create-disk=auto-delete=yes,boot=yes,device-name=korea-gpu-$RANDOM-gpu,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20240126,mode=rw,size=80,type=projects/law-2006463162/zones/asia-northeast3-c/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any


# Controller
gcloud compute instances create korea-controller-$INSTANCE_ID-2 \
    --project=law-2006463162 \
    --zone=asia-northeast3-c \
    --machine-type=e2-custom-4-8192 \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --network-interface=aliases=/26,network-tier=STANDARD,stack-type=IPV4_ONLY,subnet=subnet-korea-1 \
    --provisioning-model=STANDARD \
    --service-account=232168920061-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --create-disk=auto-delete=yes,boot=yes,device-name=korea-gpu-$RANDOM-ctrl,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20240126,mode=rw,size=80,type=projects/law-2006463162/zones/asia-northeast3-c/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any

