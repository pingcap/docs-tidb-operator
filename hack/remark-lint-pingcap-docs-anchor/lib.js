const visit = require("unist-util-visit");
const remark = require("remark");
const toString = require("mdast-util-to-string");
const slugs = require("github-slugger")();

const versionMarkPrefix = /span-classversion-mark/g;
const trailingSpan = /span$/;

function resolveHeadingSlugs(markdownContent) {
  slugs.reset();
  const anchors = [];

  function resolve() {
    return (tree) => {
      visit(tree, "heading", (node) => {
        let id;
        if (node.children.length > 0) {
          const last = node.children[node.children.length - 1];
          const match = /^(.*?)\s*\{#([\w-]+)\}$/.exec(toString(last));
          if (match && (match[1] || node.children.length > 1)) {
            id = match[2];
            if (match[1]) {
              last.value = match[1];
            } else {
              node.children.pop();
            }
          }
        }
        if (!id) {
          id = slugs.slug(toString(node), false);
        }
        const removedVersionMark = id.replace(versionMarkPrefix, "");
        anchors.push(
          removedVersionMark === id
            ? removedVersionMark
            : removedVersionMark.replace(trailingSpan, "")
        );
      });
    };
  }

  remark().use(resolve).processSync(markdownContent);
  return anchors;
}

module.exports = { resolveHeadingSlugs };
