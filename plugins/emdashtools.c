/*
 *      emdashtools.c - EmDash tools plugin (Harper, WordPress, MindMap)
 *
 *      Based on Geany's demoplugin.c pattern. GPL-2.0-or-later.
 *      Copyright 2026 tir labs inc.
 */

#ifdef HAVE_CONFIG_H
# include "config.h"
#endif

#include "geanyplugin.h"

static GtkWidget *menu_items[4] = { NULL, NULL, NULL, NULL };

static void run_tool(const gchar *cmd, const gchar *arg)
{
	GeanyDocument *doc = document_get_current();
	const gchar *fname = doc ? doc->file_name : NULL;
	gchar *out = NULL, *err = NULL;
	gint status = 0;
	gchar *argv[] = { (gchar *)cmd, (gchar *)arg, NULL };

	if (arg != NULL && (fname == NULL || *fname == '\0'))
	{
		ui_set_statusbar(FALSE, _("Save the file first."));
		return;
	}
	if (!g_spawn_sync(NULL, argv, NULL, G_SPAWN_SEARCH_PATH,
			NULL, NULL, &out, &err, &status, NULL) || status != 0)
	{
		dialogs_show_msgbox(GTK_MESSAGE_ERROR, _("Tool failed: %s"),
			err && *err ? err : cmd);
	}
	else if (out && *out)
	{
		dialogs_show_msgbox(GTK_MESSAGE_INFO, "%s", out);
	}
	g_free(out);
	g_free(err);
}

static void on_harper(GtkMenuItem *m, gpointer d) { run_tool("emdash-harper", "check"); (void)m; (void)d; }
/* Note: file arg appended by wrapper? run_tool passes single arg; publish needs file. */
static void on_harper_file(GtkMenuItem *m, gpointer d)
{
	GeanyDocument *doc = document_get_current();
	if (doc && doc->file_name)
	{
		gchar *out = NULL, *err = NULL;
		gint status = 0;
		gchar *argv[] = { "emdash-harper", "check", doc->file_name, NULL };
		if (!g_spawn_sync(NULL, argv, NULL, G_SPAWN_SEARCH_PATH,
				NULL, NULL, &out, &err, &status, NULL) || status != 0)
			dialogs_show_msgbox(GTK_MESSAGE_ERROR, _("Harper failed: %s"),
				err && *err ? err : "emdash-harper");
		else if (out && *out)
			dialogs_show_msgbox(GTK_MESSAGE_INFO, "%s", out);
		g_free(out);
		g_free(err);
	}
	else
		ui_set_statusbar(FALSE, _("Save the file first."));
	(void)m; (void)d;
}

static void on_wp_pub(GtkMenuItem *m, gpointer d)
{
	GeanyDocument *doc = document_get_current();
	if (doc && doc->file_name)
	{
		gchar *out = NULL, *err = NULL;
		gint status = 0;
		gchar *argv[] = { "emdash-wp", "publish", doc->file_name, NULL };
		if (!g_spawn_sync(NULL, argv, NULL, G_SPAWN_SEARCH_PATH,
				NULL, NULL, &out, &err, &status, NULL) || status != 0)
			dialogs_show_msgbox(GTK_MESSAGE_ERROR, _("Publish failed: %s"),
				err && *err ? err : "emdash-wp");
		else
			dialogs_show_msgbox(GTK_MESSAGE_INFO, _("Published: %s"), out ? out : "");
		g_free(out);
		g_free(err);
	}
	else
		ui_set_statusbar(FALSE, _("Save the file first."));
	(void)m; (void)d;
}

static void on_wp_list(GtkMenuItem *m, gpointer d)
{
	gchar *out = NULL, *err = NULL;
	gint status = 0;
	gchar *argv[] = { "emdash-wp", "list", NULL };
	if (!g_spawn_sync(NULL, argv, NULL, G_SPAWN_SEARCH_PATH,
			NULL, NULL, &out, &err, &status, NULL) || status != 0)
		dialogs_show_msgbox(GTK_MESSAGE_ERROR, _("Browse failed: %s"),
			err && *err ? err : "emdash-wp");
	else if (out && *out)
		dialogs_show_msgbox(GTK_MESSAGE_INFO, "%s", out);
	g_free(out);
	g_free(err);
	(void)m; (void)d;
}

static void on_mindmap(GtkMenuItem *m, gpointer d)
{
	GeanyDocument *doc = document_get_current();
	if (doc && doc->file_name)
	{
		gchar *svg = g_strconcat(doc->file_name, ".mindmap.svg", NULL);
		gchar *out = NULL, *err = NULL;
		gint status = 0;
		gchar *argv[] = { "emdash-mindmap", doc->file_name, "--out", svg, NULL };
		if (!g_spawn_sync(NULL, argv, NULL, G_SPAWN_SEARCH_PATH,
				NULL, NULL, &out, &err, &status, NULL) || status != 0)
			dialogs_show_msgbox(GTK_MESSAGE_ERROR, _("Mind map failed: %s"),
				err && *err ? err : "emdash-mindmap");
		else
		{
			gchar *uri = g_filename_to_uri(svg, NULL, NULL);
			gtk_show_uri_on_window(GTK_WINDOW(geany->main_widgets->window),
				uri, GDK_CURRENT_TIME, NULL);
			g_free(uri);
		}
		g_free(svg);
		g_free(out);
		g_free(err);
	}
	else
		ui_set_statusbar(FALSE, _("Save the file first."));
	(void)m; (void)d;
}

static gboolean emdash_tools_init(GeanyPlugin *plugin, gpointer data)
{
	GeanyData *geany_data = plugin->geany_data;
	struct { const char *label; GCallback cb; } items[] = {
		{ "Check Grammar (Harper)", G_CALLBACK(on_harper_file) },
		{ "WordPress Publish", G_CALLBACK(on_wp_pub) },
		{ "WordPress Browse", G_CALLBACK(on_wp_list) },
		{ "Mind Map", G_CALLBACK(on_mindmap) },
	};
	for (guint i = 0; i < G_N_ELEMENTS(items); i++)
	{
		menu_items[i] = gtk_menu_item_new_with_mnemonic(_(items[i].label));
		gtk_widget_show(menu_items[i]);
		gtk_container_add(GTK_CONTAINER(geany_data->main_widgets->tools_menu), menu_items[i]);
		g_signal_connect(menu_items[i], "activate", items[i].cb, plugin);
		ui_add_document_sensitive(menu_items[i]);
	}
	(void)data;
	(void)on_harper;
	return TRUE;
}

static void emdash_tools_cleanup(GeanyPlugin *plugin, gpointer data)
{
	for (guint i = 0; i < G_N_ELEMENTS(menu_items); i++)
	{
		if (menu_items[i])
			gtk_widget_destroy(menu_items[i]);
		menu_items[i] = NULL;
	}
	(void)plugin; (void)data;
}

G_MODULE_EXPORT
void geany_load_module(GeanyPlugin *plugin)
{
	plugin->info->name = "EmDash Tools";
	plugin->info->description = "Harper grammar, WordPress, and MindMap integration.";
	plugin->info->version = "1.0";
	plugin->info->author = "tir labs inc.";
	plugin->funcs->init = emdash_tools_init;
	plugin->funcs->cleanup = emdash_tools_cleanup;
	GEANY_PLUGIN_REGISTER(plugin, 226);
}
