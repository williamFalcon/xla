#pragma once

#include "torch_xla/csrc/ir.h"

namespace torch_xla {
namespace ir {
namespace ops {

class KthValue : public Node {
 public:
  KthValue(const Value& input, xla::int64 k, xla::int64 dim, bool keepdim);

  std::string ToString() const override;

  XlaOpVector Lower(LoweringContext* loctx) const override;

  xla::int64 k() const { return k_; };

  xla::int64 dim() const { return dim_; };

  bool keepdim() const { return keepdim_; }

 private:
  xla::int64 k_;
  xla::int64 dim_;
  bool keepdim_;
};

}  // namespace ops
}  // namespace ir
}  // namespace torch_xla
