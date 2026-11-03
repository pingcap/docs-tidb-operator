const path = require("path");
const fs = require("fs");
const rule = require("unified-lint-rule");
const visit = require("unist-util-visit");
const didYouMean = require("didyoumean2").default;

const lib = require("./lib");

const fileAnchors = {};

function resolveHeadingSlugs(content) {
  const slugs = lib.resolveHeadingSlugs(content);
  const result = {};
  slugs.forEach((slug) => {
    result[slug] = true;
  });
  return result;
}

function checkAnchorCurrentFile(file, node, url, currentFileAnchors) {
  const anchor = url.substring(1);
  if (currentFileAnchors[anchor] === undefined) {
    let message = `Dead anchor: ${url}`;
    const suggestion = didYouMean(anchor, Object.keys(currentFileAnchors), {
      threshold: 0.7,
    });
    if (suggestion) {
      message += `. Did you mean #${suggestion}`;
    }
    file.message(message, node);
  }
}

function checkAnchorRemoteFile(file, node, url) {
  const [relativePath, anchor] = url.split("#");
  const realPath = path.isAbsolute(relativePath)
    ? path.join(file.cwd, relativePath)
    : path.resolve(file.cwd, file.dirname, relativePath);

  try {
    fs.accessSync(realPath);
  } catch (error) {
    file.message(`Dead link: ${url}`, node);
    return;
  }

  if (fileAnchors[realPath] === undefined) {
    fileAnchors[realPath] = resolveHeadingSlugs(fs.readFileSync(realPath));
  }

  if (
    fileAnchors[realPath] === undefined ||
    fileAnchors[realPath][anchor] === undefined
  ) {
    let message = `Dead anchor: ${url}`;
    if (fileAnchors[realPath] !== undefined) {
      const suggestion = didYouMean(anchor, Object.keys(fileAnchors[realPath]), {
        threshold: 0.7,
      });
      if (suggestion) {
        message += `. Did you mean #${suggestion}`;
      }
    }
    file.message(message, node);
  }
}

function checkPingCAPDocsAnchors(ast, file) {
  const currentFileAnchors = resolveHeadingSlugs(file.contents);

  visit(ast, ["link", "definition"], (node) => {
    const url = node.url;
    if (!url || url.indexOf("//") === 0 || url.indexOf("://") > -1) {
      return;
    }
    if (url.indexOf("#") === 0) {
      checkAnchorCurrentFile(file, node, url, currentFileAnchors);
      return;
    }
    if (url.indexOf(".md") === -1 || url.indexOf("#") === -1) {
      return;
    }
    checkAnchorRemoteFile(file, node, url);
  });
}

module.exports = rule(
  "remark-lint:pingcap-docs-anchors",
  checkPingCAPDocsAnchors
);
