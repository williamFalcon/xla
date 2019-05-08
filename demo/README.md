### MNIST pytorch TPU demo

Stand-alone MNIST demo showing Pytorch on a TPU (taken from original xla tests, and simplified too run stand-alone).   

#### To run:
1. Follow the install instructions in the main readme of the xla repo.   

2. install six (in your conda env)
```bash
pip install six
```   

3. Build torchvision from source (or you'll overwrite the pytorch tpu version)
```bash
conda activate your_env   

# download and run   
git clone https://github.com/pytorch/vision.git   
cd vision
python setup.py install   
```   

4. Run the demo
```bash
conda activate your_env
python mnist.py   
```
