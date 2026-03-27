/**
 * FrameworkParser.js
 * Centralized logic for parsing and rendering structured actuarial topic frameworks.
 */

const FrameworkParser = {
    /**
     * Renders a structured content array into HTML.
     * @param {Array} content - The structured content array from JSON.
     * @param {Object} options - { query: string, recallMode: boolean, revealCallback: function }
     */
    render(content, options = {}) {
        const { query = '', recallMode = false } = options;
        
        if (!content || !Array.isArray(content)) {
            return '<div class="fwp-error">No content available.</div>';
        }

        if (recallMode) {
            return this.renderRecallCover(content, options);
        }

        let html = '<div class="fwp-container">';
        content.forEach(node => {
            html += this.renderNode(node, query);
        });
        html += '</div>';
        return html;
    },

    /**
     * Renders a single node based on its type.
     */
    renderNode(node, query) {
        const text = this.highlight(node.text || '', query);
        const bold = this.highlight(node.bold || '', query);
        const num = node.num || '';

        switch (node.type) {
            case 'h3':
                return `<div class="fwp-h3">${text}</div>`;
            case 'h4':
                return `<div class="fwp-h4">${text}</div>`;
            case 'point':
                if (bold) {
                    return `
                        <div class="fwp-point">
                            <span class="fwp-bullet"></span>
                            <div class="fwp-point-content">
                                <strong>${bold}</strong>${text ? ' — ' + text : ''}
                            </div>
                        </div>`;
                }
                return `
                    <div class="fwp-point">
                        <span class="fwp-bullet"></span>
                        <div class="fwp-point-content">${text}</div>
                    </div>`;
            case 'sub':
                return `
                    <div class="fwp-sub">
                        <span class="fwp-sub-bullet"></span>
                        <div class="fwp-sub-content">${text}</div>
                    </div>`;
            case 'numbered':
                return `
                    <div class="fwp-numbered">
                        <span class="fwp-num">${num}.</span>
                        <div class="fwp-num-content">${text}</div>
                    </div>`;
            case 'text':
            default:
                return `<div class="fwp-text">${this.inlineMarkdown(text)}</div>`;
        }
    },

    /**
     * Renders the recall cover for active recall testing.
     */
    renderRecallCover(content, options) {
        const ptCount = content.filter(n => ['point', 'sub', 'numbered'].includes(n.type)).length;
        const topicName = options.topicName || 'this topic';
        
        // We use a unique ID to handle the reveal button
        const revealId = 'reveal-' + Math.random().toString(36).substr(2, 9);
        
        return `
            <div class="fwp-recall-box" id="${revealId}">
                <div class="fwp-recall-text">🧠 Recall mode — can you recall the ${ptCount} key points for <strong>${topicName}</strong>?</div>
                <button class="fwp-reveal-btn" onclick="FrameworkParser.reveal('${revealId}', ${JSON.stringify(content).replace(/"/g, '&quot;')}, '${options.query || ''}')">Reveal</button>
            </div>`;
    },

    /**
     * Reveals the hidden content in recall mode.
     */
    reveal(containerId, content, query) {
        const container = document.getElementById(containerId);
        if (container) {
            container.outerHTML = this.render(content, { query, recallMode: false });
        }
    },

    /**
     * Highlights search query matches.
     */
    highlight(text, query) {
        if (!query || !text) return text;
        const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const re = new RegExp(`(${escapedQuery})`, 'gi');
        return text.replace(re, '<mark>$1</mark>');
    },

    /**
     * Minimal inline markdown: **bold**, *italic*, `code`
     */
    inlineMarkdown(text) {
        if (!text) return '';
        return text
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g,     '<em>$1</em>')
            .replace(/`(.+?)`/g,       '<code class="fwp-code">$1</code>');
    },

    /**
     * Helper to count points in a content array.
     */
    countPoints(content) {
        if (!content || !Array.isArray(content)) return 0;
        return content.filter(n => ['point', 'sub', 'numbered'].includes(n.type)).length;
    }
};

// Global styles for the parser
const fwpStyles = `
.fwp-container { display: flex; flex-direction: column; gap: 8px; }
.fwp-h3 { font-family: var(--mono); font-size: 11px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 8px; margin-top: 4px; }
.fwp-h4 { font-family: var(--mono); font-size: 10.5px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: .06em; margin-top: 12px; margin-bottom: 4px; padding-bottom: 4px; border-bottom: 1px solid var(--border); }
.fwp-point { display: flex; gap: 10px; align-items: flex-start; }
.fwp-bullet { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); margin-top: 8px; flex-shrink: 0; }
.fwp-point-content { font-size: 13.5px; color: var(--text); line-height: 1.6; }
.fwp-sub { display: flex; gap: 10px; align-items: flex-start; padding-left: 22px; }
.fwp-sub-bullet { width: 4px; height: 4px; border-radius: 50%; background: var(--text3); margin-top: 9px; flex-shrink: 0; }
.fwp-sub-content { font-size: 12.5px; color: var(--text2); line-height: 1.5; }
.fwp-numbered { display: flex; gap: 8px; align-items: flex-start; padding-left: 4px; }
.fwp-num { font-family: var(--mono); font-size: 12px; font-weight: 700; color: var(--accent); flex-shrink: 0; width: 18px; text-align: right; margin-top: 2px; }
.fwp-num-content { font-size: 13.5px; color: var(--text); line-height: 1.6; }
.fwp-text { font-size: 13px; color: var(--text2); line-height: 1.5; margin-left: 15px; }
.fwp-code { font-family: var(--mono); font-size: 12px; background: var(--surface3); padding: 1px 5px; border-radius: 3px; }
.fwp-recall-box { background: var(--surface3); border: 1px dashed var(--border2); border-radius: var(--radius); padding: 14px 18px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.fwp-recall-text { color: var(--text3); font-size: 13px; font-style: italic; }
.fwp-reveal-btn { font-family: var(--mono); font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 4px; cursor: pointer; background: var(--accentbg); border: 1px solid var(--accent); color: var(--accent); transition: all .2s; white-space: nowrap; }
.fwp-reveal-btn:hover { background: var(--accent); color: #fff; }
mark { background: rgba(139,92,246,0.3); color: #fff; border-radius: 2px; padding: 0 2px; }
`;

// Inject styles into document
const styleEl = document.createElement('style');
styleEl.textContent = fwpStyles;
document.head.appendChild(styleEl);
