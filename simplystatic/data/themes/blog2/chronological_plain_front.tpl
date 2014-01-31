<div class="body frontpage">
    % for pi in generatedPageInfo:
    <div class="articlebox">
        <div class="articleref">
             <a href="${pi['slug']}/">${pi['title']}</a>
             <div class="date">${pi['date']}</div>
        </div>
    </div>
    % endfor
</div>

<!-- navigation, CONDITIONAL -->
% if (nextPageUrl != None or backPageUrl != None):
    <nav class="front-nav">
        % if backPageUrl != None:
        <a href="${backPageUrl}" class="back"><i class="icon-arrow-left"></i> Back</a>
        % endif
        % if nextPageUrl != None:
        <a href="${nextPageUrl}" class="next">Next <i class="icon-arrow-right"></i></a>
        % endif
    </nav>
% endif
