#include "torch_xla/csrc/ops/bitwise_ir_ops.h"

#include "torch_xla/csrc/helpers.h"
#include "torch_xla/csrc/lowering_context.h"
#include "torch_xla/csrc/ops/ops.h"

namespace torch_xla {
namespace ir {
namespace ops {

Value BitwiseAnd(const Value& node1, const Value& node2) {
  auto lower_fn = [](const Node& node, LoweringContext* loctx) -> XlaOpVector {
    xla::XlaOp op0 = loctx->GetOutputOp(node.operand(0));
    xla::XlaOp op1 = loctx->GetOutputOp(node.operand(1));
    auto kernel = [](const xla::XlaOp& op0, const xla::XlaOp& op1) {
      return op0 & op1;
    };
    return node.ReturnOp(XlaHelpers::PromotedBinaryOp(op0, op1, kernel), loctx);
  };
  return GenericOp(OpKind(at::aten::__and__), OpList{node1, node2},
                   node1.shape(), std::move(lower_fn));
}

Value BitwiseOr(const Value& node1, const Value& node2) {
  auto lower_fn = [](const Node& node, LoweringContext* loctx) -> XlaOpVector {
    xla::XlaOp op0 = loctx->GetOutputOp(node.operand(0));
    xla::XlaOp op1 = loctx->GetOutputOp(node.operand(1));
    auto kernel = [](const xla::XlaOp& op0, const xla::XlaOp& op1) {
      return op0 | op1;
    };
    return node.ReturnOp(XlaHelpers::PromotedBinaryOp(op0, op1, kernel), loctx);
  };
  return GenericOp(OpKind(at::aten::__or__), OpList{node1, node2},
                   node1.shape(), std::move(lower_fn));
}

Value BitwiseXor(const Value& node1, const Value& node2) {
  auto lower_fn = [](const Node& node, LoweringContext* loctx) -> XlaOpVector {
    xla::XlaOp op0 = loctx->GetOutputOp(node.operand(0));
    xla::XlaOp op1 = loctx->GetOutputOp(node.operand(1));
    auto kernel = [](const xla::XlaOp& op0, const xla::XlaOp& op1) {
      return op0 ^ op1;
    };
    return node.ReturnOp(XlaHelpers::PromotedBinaryOp(op0, op1, kernel), loctx);
  };
  return GenericOp(OpKind(at::aten::__xor__), OpList{node1, node2},
                   node1.shape(), std::move(lower_fn));
}

}  // namespace ops
}  // namespace ir
}  // namespace torch_xla
