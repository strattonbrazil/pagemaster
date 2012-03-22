package com.scbots.pagemaster;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.util.Log;
import android.view.View;

public class PageMasterActivity extends Activity {
	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		Log.e("foo", "just here");
		
		
		// List<E> resource file
		//
		List<View> pageViews = new ArrayList<View>();
		InputStream bookInfoStream = null;
		try {
			bookInfoStream = getAssets().open("book.xml");
			
			DocumentBuilderFactory builderFactory = DocumentBuilderFactory.newInstance();
			DocumentBuilder builder = null;
			try {
				builder = builderFactory.newDocumentBuilder();
				
				try {
					Document document = builder.parse(bookInfoStream);
					Element rootElement = document.getDocumentElement();
					NodeList nodes = rootElement.getChildNodes();

					for(int i=0; i<nodes.getLength(); i++){
						Node node = nodes.item(i);

						if(node instanceof Element){
							//a child element to process
							Element child = (Element)node;
							if (child.getNodeName().matches("page")) {
								String imageKey = child.getAttribute("imageKey");
								int numImages = Integer.parseInt(child.getAttribute("numImages"));
								int delay = Integer.parseInt(child.getAttribute("delay"));
								
								Bitmap[] images = new Bitmap[numImages];
								for (int j = 0; j < numImages; j++) {
									String fileName = imageKey + (j+1) + ".png";
									InputStream stream = null;
									try {
										stream = getAssets().open(fileName);
										images[j] = BitmapFactory.decodeStream(stream);
									} catch (IOException e) {
										e.printStackTrace();
									}

								}
								pageViews.add(new PageView(this, images, delay));
							}
						}
					}
				} catch (SAXException e) {
					e.printStackTrace();
				} catch (IOException e) {
					e.printStackTrace();
				}

			} catch (ParserConfigurationException e) {
				e.printStackTrace();  
			}

		} catch (IOException e) {
			e.printStackTrace();
		}


		setContentView(pageViews.get(0));


		//for (String local : getAssets().getLocales())
		//	Log.e("foo", local);

		
		//System.out.println(images[0]);
		//stream = getAssets().open("piggy.gif");

		//GifMovieView view = new GifMovieView(this, stream);
		//GifWebView view = new GifWebView(this, "file:///android_asset/piggy.gif");
		//
		//setContentView(view);
		//setContentView(view);

		//setContentView(R.layout.main);
	}
}
