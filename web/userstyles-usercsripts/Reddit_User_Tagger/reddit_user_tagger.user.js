// ==UserScript==
// @name          Reddit User Tagger
// @namespace 	  http://www.reddit.com/
// @description	  Tag your enemies or friends...
// @author        honestbleeps
// @include       http://reddit.com/*
// @include       https://reddit.com/*
// @include       http://*.reddit.com/*
// @include       https://*.reddit.com/*
// ==/UserScript==

function insertAfter( referenceNode, newNode ) {
	if ((typeof(referenceNode.parentNode) != 'undefined') && (typeof(referenceNode.nextSibling) != 'undefined')) {
		referenceNode.parentNode.insertBefore( newNode, referenceNode.nextSibling );
	}
}
function setUserTag(obj, username) {
	var thisTag = prompt("User tag for " + username, localStorage.getItem(username));
	if (thisTag.length > 0) {
		localStorage.setItem(username, thisTag);
		obj.innerHTML = thisTag;
	} else {
		localStorage.removeItem(username);
		obj.innerHTML = '_';
	}
	return false;
}

(function(u) {
	var a = document.querySelectorAll('.entry a.author'), i;

	for (i in a) {
			var userTag = document.createElement('span');
			var userTagLink = document.createElement('a');
			thisTag = localStorage.getItem(a[i].text);
			if (!(thisTag)) thisTag = '_';
			userTagLink.setAttribute('class','userTagLink');
			userTagLink.innerHTML = thisTag;
			// userTagLink.setAttribute('onClick','javascript:setUserTag(this, \'' + a[i].text + '\')');
			userTagLink.setAttribute('username',a[i].text);
			userTagLink.setAttribute('title','set a tag');
			userTagLink.setAttribute('href','javascript:void(0)');
			userTag.appendChild(userTagLink);
			userTag.innerHTML = ' (' + userTag.innerHTML + ')';
			insertAfter( a[i], userTag );
	}

	var a = document.querySelectorAll('a.userTagLink'), i;
	for (i in a) {
		a[i].addEventListener('click',function(e) {
				setUserTag(this, this.getAttribute('username'));
		}, true);
	}
})();
