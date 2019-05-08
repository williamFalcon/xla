import os
import shutil
import time
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
import torch_xla
import torch_xla_py.data_parallel as dp
import torch_xla_py.utils as xu
import torch_xla_py.xla_model as xm

datadir='/tmp/mnist-data'
batch_size=128
target_accuracy=98.0
num_workers = 1
num_epochs = 100
metrics_debug = True

class MNIST(nn.Module):

  def __init__(self):
    super(MNIST, self).__init__()
    self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
    self.bn1 = nn.BatchNorm2d(10)
    self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
    self.bn2 = nn.BatchNorm2d(20)
    self.fc1 = nn.Linear(320, 50)
    self.fc2 = nn.Linear(50, 10)

  def forward(self, x):
    x = F.relu(F.max_pool2d(self.conv1(x), 2))
    x = self.bn1(x)
    x = F.relu(F.max_pool2d(self.conv2(x), 2))
    x = self.bn2(x)
    x = x.view(-1, 320)
    x = F.relu(self.fc1(x))
    x = self.fc2(x)
    return F.log_softmax(x, dim=1)


def train_mnist():
  torch.manual_seed(1)
  # Training settings
  lr = 0.01
  momentum = 0.5

  train_loader = torch.utils.data.DataLoader(
      datasets.MNIST(
          datadir,
          train=True,
          download=True,
          transform=transforms.Compose([
              transforms.ToTensor(),
              transforms.Normalize((0.1307,), (0.3081,))
          ])),
      batch_size=batch_size,
      shuffle=True,
      num_workers=num_workers)
  test_loader = torch.utils.data.DataLoader(
      datasets.MNIST(
          datadir,
          train=False,
          transform=transforms.Compose([
              transforms.ToTensor(),
              transforms.Normalize((0.1307,), (0.3081,))
          ])),
      batch_size=batch_size,
      shuffle=True,
      num_workers=num_workers)

  devices = xm.get_xla_supported_devices()
  # Pass [] as device_ids to run using the PyTorch/CPU engine.
  model_parallel = dp.DataParallel(MNIST, device_ids=devices)

  def train_loop_fn(model, loader, device, context):
    loss_fn = nn.NLLLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=momentum)
    tracker = xm.RateTracker()

    for x, (data, target) in loader:
      optimizer.zero_grad()
      output = model(data)
      loss = loss_fn(output, target)
      loss.backward()
      xm.optimizer_step(optimizer)
      tracker.add(batch_size)
      print('[{}]({}) Loss={:.5f} Rate={:.2f}'.format(device, x, loss.item(),
                                                      tracker.rate()))

  def test_loop_fn(model, loader, device, context):
    total_samples = 0
    correct = 0
    for x, (data, target) in loader:
      output = model(data)
      pred = output.max(1, keepdim=True)[1]
      correct += pred.eq(target.view_as(pred)).sum().item()
      total_samples += data.size()[0]

    print('[{}] Accuracy={:.2f}%'.format(device,
                                         100.0 * correct / total_samples))
    return correct / total_samples

  accuracy = 0.0
  for epoch in range(1, num_epochs + 1):
    model_parallel(train_loop_fn, train_loader)
    accuracies = model_parallel(test_loop_fn, test_loader)
    accuracy = sum(accuracies) / len(devices)
    if metrics_debug:
      print(torch_xla._XLAC._xla_metrics_report())

  return accuracy * 100.0

if __name__ == '__main__':
  train_mnist()
