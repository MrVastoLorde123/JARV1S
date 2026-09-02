"""Core package namespace.

Keep package initialization side-effect free so importing one core module does
not eagerly import higher-level execution boundaries or create dependency
cycles across context, agency, and plugin layers.
"""
